import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore, Thread

from rainbow.optical_flow.model_factory import ModelFactory

from torch import Tensor
from torch.multiprocessing import Manager, Process, set_start_method


class ModelManager:
    """Manager for optical flow models.

    Initializes a CPU or CUDA based optical flow model (class that inherits
    rainbow.optical_flow.base_model.BaseModel) and provides a proxy to it.
    The proxy has the same functionality as the original model but instances of
    the proxy can now be passed to separate Python worker processes, e.g.
    without pickling errors, while allowing the single optical flow model
    instance to be shared between them, e.g. without duplicating the model in
    memory. Solves issues such as (1)
    https://github.com/pytorch/pytorch/issues/16943#issuecomment-462956544 and
    (2)
    https://github.com/pytorch/pytorch/issues/35472#issuecomment-879141708.
    Additionally, automatically manages the lifecycle of the model, such as
    batch image inference from multiple worker processes and model termination.
    """
    _sentinel = 'STOP'

    def __init__(self, model_name, model_config, max_num_parl_preds=1,
                 num_proxies=1):
        """Initializes the manager.

        Args:
            model_name (string): The name of the optical flow model to manage.
            model_config (dict): The config of the optical flow model.
            max_num_parl_preds (int, optional): The maximum number of image
                sequences that can be fed to the optical flow model
                simultaneously. Defaults to 1.
            num_proxies (int, optional): The number of optical flow model proxy
            instances to create. Defaults to 1.
        """
        set_start_method('spawn', force=True)  # for CUDA support
        model_factory = ModelFactory()
        self._model = model_factory.get_model(model_name, model_config)
        self._max_num_parl_preds = max_num_parl_preds
        self._queues = [Manager().Queue() for _ in range(0, num_proxies)]

    def start(self):
        """Creates the model proxy instances for use, loads the model into
           memory and begins managing the model.
        """
        self._models = [ModelProxy(self._model, queue) for queue in
                        self._queues]
        self._process = Process(target=self)
        self._process.start()

    def stop(self):
        """Releases the model from memory and shuts the manager down."""
        for queue in self._queues:
            queue.put(self._sentinel)

        self._process.join()

    @property
    def models(self):
        """list: Gets the model proxy instances."""
        return self._models

    def __call__(self):
        self._model.load()
        asyncio.run(self._main_worker())

    async def _main_worker(self):
        self._semaphore = Semaphore(self._max_num_parl_preds)
        executor = ThreadPoolExecutor(len(self._queues))
        event_loop = asyncio.get_event_loop()
        await asyncio.gather(*[self._listen(queue, executor, event_loop)
                               for queue in self._queues])

    async def _listen(self, queue, executor, event_loop):
        while True:
            if isinstance((rcvd := await event_loop.run_in_executor(
                    executor, queue.get)), Tensor):
                thread = Thread(target=self._run, args=(rcvd, queue,))
                thread.start()
            elif rcvd == self._sentinel:
                break

    def _run(self, imgs, queue):
        self._semaphore.acquire()
        preds = self._model.run(imgs)  # exceptions?
        self._semaphore.release()
        queue.put(preds)


class ModelProxy:
    """Proxy for optical flow model of type
       rainbow.optical_flow.model.Model managed by
       rainbow.optical_flow.model_manager.ModelManager.
    """
    def __init__(self, model, queue):
        """Initializes the proxy.

        Args:
            model (BaseModel): Optical flow model to create the proxy for.
            queue (torch.multiprocessing.Manager.Queue): Queue to use for
                communicating with a Python worker process containing the
                optical flow model.
        """
        self._queue = queue
        self._prepare = model.prepare

    def prepare(self, imgs):
        """Proxy method for the '.prepare()' method of the optical flow
           model.
        """
        return self._prepare(imgs)

    def run(self, imgs):
        """Proxy method for the '.run()' method of the optical flow model."""
        self._queue.put(imgs)
        preds = self._queue.get()

        return preds

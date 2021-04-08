import os
from multiprocessing import Process, Queue
from pathlib import Path

from rainbow.data_analysis import analyze_data
from rainbow.optical_flow.opt_flow import compute_opt_flow
from rainbow.util import load_nd2_imgs, load_std_imgs


def process_files(root_dir, config, num_wrkers, recursive):
    queue = Queue(config['q_sz'])
    procs, num_wrkers = initialize_workers(num_wrkers, config, queue)
    curr_img_batch, img_batches = [], []
    for root_dir, dirs, files in os.walk(root_dir):
        img_paths = [root_dir]
        img_paths += [os.path.join(root_dir, f) for f in files if
                      Path(f).suffix == '.nd2']
        for img_path in img_paths:
            imgs = ([load_std_imgs(img_path, config['mpp'])] if
                    os.path.isdir(img_path) else load_nd2_imgs(img_path,
                    config['nd2']))
            if len(imgs[0]) == 0:
                continue
            for img_ser in imgs:
                curr_img_batch.append(img_ser)
                if len(curr_img_batch) == config['proc_bch_sz']:
                    img_batches.append(curr_img_batch)
                    curr_img_batch = []
                    if len(img_batches) == config['max_qd_bches']:
                        process_img_batches(img_batches, config, queue)
                        img_batches = []
        if not recursive:
            break

    img_batches.append(curr_img_batch)
    process_img_batches(img_batches, config, queue)
    queue.put([None])
    for proc in procs:
        proc.join()


def initialize_workers(num_wrkers, config, queue):
    if num_wrkers == -1:
        num_wrkers = os.cpu_count() if os.cpu_count() is not None else 1

    procs = []
    for i in range(0, num_wrkers):
        proc = Process(target=analyze_data, args=(queue, config))
        proc.daemon = True
        procs.append(proc)

    for proc in procs:
        proc.start()

    return procs, num_wrkers


def process_img_batches(img_batches, config, queue):
    data = compute_opt_flow(img_batches, config)
    for d_bch in data:
        queue.put(d_bch)

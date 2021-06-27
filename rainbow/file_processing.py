import os
from multiprocessing import Process, Queue
from pathlib import Path

from rainbow.data_analysis import analyze_data
from rainbow.optical_flow.optical_flow import compute_opt_flow
from rainbow.util import load_nd2_imgs, load_std_imgs


def process_files(root_dir, config, num_wrkers, recursive, debug,
                  overwrite_flow):
    queue = Queue(config['q_sz'])
    if not debug:
        procs = initialize_workers(num_wrkers, config, queue)
    curr_img_batch, img_batches = [], []
    for root_dir, dirs, files in os.walk(root_dir):
        img_paths = [root_dir]
        img_paths += [os.path.join(root_dir, f) for f in files if
                      Path(f).suffix == '.nd2']
        for img_path in img_paths:
            imgs = ([load_std_imgs(img_path, config['mpp'])] if
                    os.path.isdir(img_path) else load_nd2_imgs(img_path,
                    config['nd2'], config['mpp']))
            if len(imgs[0]) == 0:
                continue
            for img_ser in imgs:
                curr_img_batch.append(img_ser)
                if len(curr_img_batch) == config['proc_bch_sz']:
                    img_batches.append(curr_img_batch)
                    curr_img_batch = []
                    if len(img_batches) == config['max_qd_bches']:
                        process_img_batches(img_batches, config, queue, debug,
                                            overwrite_flow)
                        img_batches = []
        if not recursive:
            break

    img_batches.append(curr_img_batch)
    process_img_batches(img_batches, config, queue, debug, overwrite_flow)

    if not debug:
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

    return procs


def process_img_batches(img_batches, config, queue, debug, overwrite_flow):
    output_dirs = compute_opt_flow(img_batches, config, save_raw_imgs=True,
                                   overwrite_flow=overwrite_flow)
    for output_dirs_bch in output_dirs:
        queue.put(output_dirs_bch)
    if debug:
        queue.put([None])
        analyze_data(queue, config)
        queue.get()

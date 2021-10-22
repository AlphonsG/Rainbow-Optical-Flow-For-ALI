import os
from multiprocessing import Process, Queue
from pathlib import Path

from rainbow.data_analysis import analyze_data
from rainbow.optical_flow.optical_flow import compute_opt_flow
from rainbow.util import load_nd2_imgs, load_std_imgs

SENTINEL = 'STOP'


def process_files(root_dir, config, num_wrkrs, recursive, debug,
                  overwrite_flow):
    queue = Queue(config['q_sz'])
    if not debug:
        wrkrs = initialize_workers(num_wrkrs, config, queue)
    for curr_dir, dirs, files in os.walk(root_dir):
        img_paths = [curr_dir] + [os.path.join(curr_dir, f) for f in files if
                                  Path(f).suffix == '.nd2']
        for img_path in img_paths:
            imgs = ([load_std_imgs(img_path, config['mpp'])] if
                    os.path.isdir(img_path) else load_nd2_imgs(img_path,
                    config['nd2'], config['mpp']))
            if len(imgs[0]) == 0:
                continue
            for img_ser in imgs:
                output_dir = compute_opt_flow(img_ser, config,
                                              save_raw_imgs=True,
                                              overwrite_flow=overwrite_flow)
                queue.put(output_dir)
                if debug:
                    queue.put(SENTINEL)
                    analyze_data(queue, config)
        if not recursive:
            break

    if not debug:
        queue.put(SENTINEL)
        for wrkr in wrkrs:
            wrkr.join()


def initialize_workers(num_wrkrs, config, queue):
    if num_wrkrs is None:
        num_wrkrs = os.cpu_count() if os.cpu_count() is not None else 1

    wrkrs = []
    for i in range(0, num_wrkrs):
        wrkr = Process(target=analyze_data, args=(queue, config))
        wrkr.daemon = True
        wrkrs.append(wrkr)

    for wrkr in wrkrs:
        wrkr.start()

    return wrkrs

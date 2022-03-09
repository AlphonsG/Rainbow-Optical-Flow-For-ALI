import os
from multiprocessing import Process, Queue
from pathlib import Path

from rainbow import OPTICAL_FLOW_FILENAME
from rainbow.data_analysis import analyze_data
from rainbow.optical_flow.optical_flow import compute_optical_flow
from rainbow.util import load_nd2_imgs, load_std_imgs

from tqdm import tqdm

SENTINEL = 'STOP'


def process_files(root_dir, config, num_wrkrs, subdirs, overwrite_flow):
    """Processes files located within root_dir.

    Finds valid files (image sequences) within root_dir from which to compute
    the optical flow from and perform data analysis.

    Args:
        root_dir (string): The path to an existing directory containing image
            sequences as .nd2 files or 2 or more image files in common formats
            (.png, .tiff, etc).
        config (string): The path to a .yaml configuration file.
        num_wrkrs (int): The number of workers to use for parallel analysis.
            If set to None will use the same number of workers as CPU core
            count.
        subdirs (bool): If True, will look for image sequences in root_dir
            subfolders instead of top level directory.
        overwrite_flow (bool): If True, will compute optical flow
            even if a flow file already exists for an image sequence.
    """
    queue = Queue()
    if num_wrkrs != 1:
        wrkrs = initialize_workers(num_wrkrs, config, queue)

    try:
        dirs = [os.path.join(root_dir, curr_dir) for curr_dir in
                next(os.walk(root_dir))[1]] if subdirs else [root_dir]
    except StopIteration:
        print(f'Root directory ({root_dir}) is empty.')

    pbar = tqdm(total=1)
    for curr_dir in dirs:
        try:
            files = next(os.walk(curr_dir))[2]
        except StopIteration:
            files = []
        img_paths = [curr_dir] + [os.path.join(curr_dir, f) for f in files if
                                  Path(f).suffix == '.nd2']
        for img_path in img_paths:
            imgs = ([load_std_imgs(img_path, config['mpp'])] if
                    os.path.isdir(img_path) else load_nd2_imgs(img_path,
                    config['nd2'], config['mpp']))
            if len(imgs[0]) == 0:
                continue

            pbar.total += len(imgs)
            pbar.refresh()
            for img_seq in imgs:
                if len(img_seq) < 2:
                    pbar.update()
                    continue
                output_dir = get_output_dir(img_seq, config)
                if not skip_opt_flow(output_dir, overwrite_flow):
                    compute_optical_flow(img_seq, output_dir, config[
                        'opt_flow_model'], config[config['opt_flow_model']],
                        overwrite_flow=overwrite_flow)

                queue.put(output_dir)
                if num_wrkrs == 1:
                    queue.put(SENTINEL)
                    analyze_data(queue, config)
                    queue.get()

                pbar.update()

        if not subdirs:
            break

    if num_wrkrs != 1:
        queue.put(SENTINEL)
        for wrkr in wrkrs:
            wrkr.join()
        pbar.update()
    else:
        pbar.update()

    pbar.close()


def initialize_workers(num_wrkrs, config, queue):
    """Initializes workers.

    Creates and starts workers (subprocesses) that will perfrom data analysis.

    Args:
        num_wrkrs (int): The number of workers to create. If set to None will
        create the same number of workers as CPU core count.
        config (string): The path to a .yaml configuration file.
        queue (multiprocessing.Queue): The queue that will be used to
            communicate with the workers.

    Returns:
        list: A list of initalized workers as multiprocessing.Process objects.
    """
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


def get_output_dir(imgs, config):
    """Determines the corresponding output directory for an image sequence.

    The automatically named output directory will be used to store the
    data generated from an image sequence and is not created if
    nonexisting.

    Args:
        imgs (list): An image sequence as a list of PIMS Frame arrays.
        config (string): The path to a .yaml configuration file.

    Returns:
        string: The path to the output directory.
    """
    name, ext = os.path.splitext(imgs[0].metadata['img_name'])
    ser = ('_Series_{})'.format(imgs[0].metadata[config['nd2'][
           'naming_axs'][0]]) if ext == '.nd2' else '')
    output_dir = '{}_{}{}_etc'.format(ext.replace('.', ''), name, ser)
    output_dir = output_dir.replace(' ', '_')
    output_dir = os.path.join(imgs[0].metadata['img_ser_md']['dir'],
                              output_dir)

    return output_dir


def skip_opt_flow(output_dir, overwrite_flow):
    """Determines whether optical flow computation should be skipped.

    Skips computation iff an optical flow file already exists in output_dir
    and optical flow is not set to be overwritten.

    Args:
        output_dir (string): The path to an existing output directory.
        overwrite_flow (bool): If True, will ignore optical flow file if
            already existing in output_dir.

    Returns:
        bool: Whether optical flow computation should be skipped.
    """
    return True if not overwrite_flow and (Path(output_dir) / (
        OPTICAL_FLOW_FILENAME)).is_file() else False

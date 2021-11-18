import json
import os
import shutil
import warnings
from datetime import datetime
from pathlib import Path

import cv2

from moviepy.editor import ImageSequenceClip

from natsort import natsorted

from nd2reader import ND2Reader

import numpy as np

from pims import Frame

import rainbow

VID_FILE_EXT = '.mp4'


def load_nd2_imgs(nd2, axs_config, mpp=None):  # mpp None?
    """Loads image sequences from a .nd2 file.

    Args:
        nd2 (string): The path to a .nd2 file.
        axs_config (dict): A dictionary with the key 'iter_axs', containing a
            list of the ordered nd2 axes to iterate over, and the key
            'bdl_axs', containing a list of the axes to bundle when iterating.
        mpp (float, optional): The micrometres per pixel value of the
            image sequences, if missing from the .nd2 file. Defaults to None.

    Returns:
        list: A list of image sequences loaded from the .nd2 file.
    """
    frms = ND2Reader(nd2)
    avl_axs = list(frms.sizes.keys())
    iter_axs = [ax for ax in axs_config['iter_axs'] if ax in avl_axs]
    bdl_axs = [ax for ax in axs_config['bdl_axs'] if ax in avl_axs]
    if len(iter_axs) == 0 or len(bdl_axs) == 0:
        return []
    frms.iter_axes, frms.bundle_axes = ''.join(iter_axs), ''.join(bdl_axs)
    min_px, max_px, ser_len = (0, np.array(list(frms)).max(),
                               frms.sizes[iter_axs[-1]])
    imgs, curr_img_ser = [], []
    for i, frm in enumerate(frms):
        img = (frm.astype(float) - min_px) * 255.0 / (max_px - min_px)
        img = np.asarray(img, dtype=np.uint8)
        img = img[:, :, np.newaxis]
        img = np.repeat(img, 3, axis=2)
        frame = Frame(img)
        frame.metadata = frm.metadata
        frame.metadata['type'] = '.nd2'
        frame.metadata['path'] = nd2
        frame.metadata['img_name'] = 'Image_{}.png'.format(
            frm.metadata['coords'][axs_config['iter_axs'][-1]])
        try:
            frame.metadata['mpp'] = frame.metadata['pixel_microns']
        except KeyError:
            frame.metadata['mpp'] = mpp

        curr_img_ser.append(frame)
        if (i + 1) % ser_len == 0:
            curr_img_ser[0].metadata['img_ser_md'] = frms.metadata
            curr_img_ser[0].metadata['img_ser_md']['type'] = '.nd2'
            curr_img_ser[0].metadata['img_ser_md']['dir'] = os.path.dirname(
                nd2)
            imgs.append(curr_img_ser)
            curr_img_ser = []

    frms.close()

    return imgs


def load_std_imgs(input_dir, mpp=None):
    """Loads an image sequence from input_dir.

    Assumes order of image sequence corresponds to naturally sorted image
    filenames in input_dir.

    Args:
        input_dir (string): The path to the input directory.
        mpp (float, optional): The micrometres per pixel value of the
            image sequence. Defaults to None.

    Returns:
        list: A list of images.
    """
    try:
        _, _, files = next(os.walk(input_dir))
    except StopIteration:
        return []

    files = natsorted([os.path.join(input_dir, f) for f in files])
    imgs = []
    for f in files:
        img = cv2.imread(f)
        if img is not None:
            frame = Frame(img)
            frame.metadata['type'], frame.metadata['path'], frame.metadata[
                'img_name'], frame.metadata['mpp'] = (Path(f).suffix, f,
                                                      Path(f).name, mpp)  # mp?

            if len(imgs) == 0:
                frame.metadata['img_ser_md'] = {'type': Path(f).suffix,
                                                'dir': input_dir,
                                                'calibration_um': mpp
                                                }
            imgs.append(frame)

    return imgs


def save_img_ser(imgs, output_dir, use_metadata_name=True):
    """Saves an image sequence to output_dir.

    Saves images in .png format. Automatically names image files or uses
    stored image names in image sequence metadata.

    Args:
        imgs (list): A list of images.
        output_dir (string): The path to the output directory.
        use_metadata_name (bool, optional): If True, names images using image
            names in sequence metadata. Defaults to True.
    """
    for i, img in enumerate(imgs):
        path = (os.path.join(output_dir, img.metadata['img_name']) if
                use_metadata_name else os.path.join(output_dir,
                'Image_{}.png'.format(i)))
        cv2.imwrite(path, img)


def cleanup_dir(output_dir):
    """Cleans up output_dir.

    If output_dir exists, attempts to remove it and its contents.

    Args:
        output_dir (string): The path to a directory.

    Returns:
        bool: If True, output_dir is guaranteed not to exist.
    """
    if os.path.isdir(output_dir):
        try:
            shutil.rmtree(output_dir)
        except OSError as e:
            msg = (f'Could not remove existing directory ({output_dir}), '
                   f'reason: {str(e)}.')
            warnings.warn(msg, UserWarning)
            return False

    return True


def comb_imgs(img1, img2):
    """Horizontally concatenates two images.

    img1 becomes the leftmost image, while img2 becomes the rightmost image.

    Args:
        img1 (numpy.array): An image.
        img2 (numpy.array): An image.

    Returns:
        numpy.array: Image result of horizontally concatenating the two images.
    """
    return np.concatenate((img1, img2), axis=1)


def save_video(input_dir, output_path, fps=5):
    """Saves a video.

    Saves a video generated from an image sequence, located in input_dir,
    to output_path.

    Args:
        input_dir (string): The path to the input directory.
        output_path (string): The path to write the generated video to
            (includes video filename without extension).
        fps (int, optional): The framerate of the generated video. Defaults
            to 5.

    Returns:
        bool: If True, video was successfully saved.
    """
    imgs = load_std_imgs(input_dir)
    if len(imgs) == 0:
        return False

    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg is not None:
        os.environ['FFMPEG_BINARY'] = ffmpeg

    os.environ['FFREPORT'] = 'file='
    video = ImageSequenceClip([cv2.cvtColor(img, cv2.COLOR_BGR2RGB) for img in
                               imgs], fps=fps)
    video.write_videofile(os.path.join(output_path + VID_FILE_EXT),
                          logger=None, write_logfile=False)
    video.close()

    return True


def apply_metadata(img1, img2):
    """Sets img1's metadata to that of img2.

    Args:
        img1 (PIMS Frame): An image with a 'metadata' attribute.
        img2 (numpy.array): An image.

    Returns:
        PIMS Frame: An image.
    """
    img1 = Frame(img1)
    img1.metadata = img2.metadata

    return img1


def save_optical_flow(preds, output_dir):
    """Saves optical flow predictions to a file in output_dir.

    Args:
        preds (list): A list of optical flow predictions as numpy arrays.
        output_dir (string): The path to the output directory.
    """
    np.save(os.path.join(output_dir, rainbow.OPTICAL_FLOW_FILENAME),
            np.array(preds), allow_pickle=False)


def load_optical_flow(flow_path):
    """Loads optical flow predictions from a file.

    Args:
        flow_path (string): The path to a .npy file containing saved optical
            flow predictions.

    Returns:
        list: A list of optical flow predictions as numpy arrays.
    """
    raw_preds = np.load(flow_path)
    preds = []
    for i in range(0, raw_preds.shape[0]):
        preds.append(raw_preds[i, ...])

    return preds


def save_img_ser_metadata(imgs, output_dir):
    """Saves image sequence metadata to a .json file in output_dir.

    Args:
        imgs (list): A list of images as PIMS Frame arrays.
        output_dir (string): The path to the output directory.
    """
    metadata = imgs[0].metadata['img_ser_md']
    now = datetime.now()
    dt_str = now.strftime('%d %B %Y, %H:%M:%S')
    metadata['analysis_timestamp'] = dt_str
    with open(os.path.join(output_dir, f'{rainbow.METADATA_FILENAME}.json'),
              'w') as f:
        json.dump(metadata, f, indent=4, sort_keys=True, default=str)


def video_reshape(vid_path, set_wdh=None):
    """Resizes a video.

    Calculates the video dimensions of a video, while maintaining the aspect
    ratio, if the width were resized.


    Args:
        vid_path (string): The path to a video file.
        set_wdh (int, optional): The new width of the video. Defaults to None.

    Returns:
        int, int: The new width and height of the video.
    """
    cap = cv2.VideoCapture(vid_path)
    hgt, wdh, _ = cap.read()[1].shape
    dsp_wdh = set_wdh if set_wdh is not None else wdh
    dsp_hgt = dsp_wdh * (hgt / wdh) if wdh is not None else hgt
    cap.release()

    return round(dsp_wdh), round(dsp_hgt)

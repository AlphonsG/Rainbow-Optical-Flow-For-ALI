import json
import os
import shutil
import warnings
from datetime import datetime
from pathlib import Path

import cv2

from moviepy.editor import ImageSequenceClip

from natsort import natsorted

import numpy as np

from pims import Frame, ND2Reader_SDK as ND2_Reader

import rainbow

VID_FILE_EXT = '.mp4'


def load_nd2_imgs(nd2, axs_config, mpp=None):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        frms = ND2_Reader(nd2)

    avl_axs = list(frms.sizes.keys())
    iter_axs = [ax for ax in axs_config['iter_axs'] if ax in avl_axs]
    bdl_axs = [ax for ax in axs_config['bdl_axs'] if ax in avl_axs]
    if len(iter_axs) == 0 or len(bdl_axs) == 0:
        return []
    frms.iter_axes, frms.bundle_axes = ''.join(iter_axs), ''.join(bdl_axs)
    min_px, max_px, ser_len = 0, frms.max_value, frms.sizes[iter_axs[-1]]
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
        frame.metadata['img_name'] = ('Image_{}.png'.format(frm.metadata[
                                      axs_config['iter_axs'][-1]]))
        if 'mpp' not in frame.metdata:
            frame.metadata['mpp'] = mpp

        if i == 0 or i % ser_len != 0:
            curr_img_ser.append(frame)
        else:
            curr_img_ser[0].metadata['img_ser_md'] = frms.metadata
            curr_img_ser[0].metadata['img_ser_md']['type'] = '.nd2'
            curr_img_ser[0].metadata['img_ser_md']['dir'] = (
                os.path.dirname(nd2))
            imgs.append(curr_img_ser)
            curr_img_ser = [frame]

    frms.close()

    return imgs


def load_std_imgs(input_dir, mpp=None):
    _, _, files = next(os.walk(input_dir))
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


def save_img_ser(imgs, output_dir, auto_name=True):
    for i, img in enumerate(imgs):
        path = (os.path.join(output_dir, img.metadata['img_name']) if
                auto_name else os.path.join(output_dir, 'Image_{}.png'.format(
                    i)))
        cv2.imwrite(path, img)


def cleanup_dir(output_dir):
    if os.path.isdir(output_dir):
        try:
            shutil.rmtree(output_dir)
        except OSError as e:
            msg = ('Could not remove existing image directory ({}), '
                   'skipping image writing, reason: {}'.format(output_dir,
                                                               str(e)))
            warnings.warn(msg, UserWarning)

            return False

    return True


def comb_imgs(img1, img2, axis=1):
    return np.concatenate((img1, img2), axis=axis)


def save_video(input_dir, output_path, fps=5):
    imgs = load_std_imgs(input_dir)
    if len(imgs) == 0:
        return False

    os.environ['FFREPORT'] = 'file='
    video = ImageSequenceClip([cv2.cvtColor(img, cv2.COLOR_BGR2RGB) for img in
                               imgs], fps=fps)
    video.write_videofile(os.path.join(output_path + VID_FILE_EXT),
                          logger=None, write_logfile=False)


def apply_metadata(img1, img2):
    img1 = Frame(img1)
    img1.metadata = img2.metadata

    return img1


def save_optical_flow(preds, output_dir):
    np.save(os.path.join(output_dir, f'{rainbow.OPTICAL_FLOW_FILENAME}.npy'),
            np.array(preds),
            allow_pickle=False)


def load_optical_flow(flow_path):
    raw_preds = np.load(flow_path)
    preds = []
    for i in range(0, raw_preds.shape[0]):
        preds.append(raw_preds[i, ...])

    return preds


def save_img_ser_metadata(imgs, output_dir):
    metadata = imgs[0].metadata['img_ser_md']
    now = datetime.now()
    dt_str = now.strftime('%d %B %Y, %H:%M:%S')
    metadata['analysis_timestamp'] = dt_str
    with open(os.path.join(output_dir, f'{rainbow.METADATA_FILENAME}.json'),
              'w') as f:
        json.dump(metadata, f, indent=4, sort_keys=True, default=str)


def video_reshape(vid_path, set_wdh=None):
    cap = cv2.VideoCapture(vid_path)
    hgt, wdh, _ = cap.read()[1].shape
    dsp_wdh = set_wdh if set_wdh is not None else wdh
    dsp_hgt = dsp_wdh * (hgt / wdh) if wdh is not None else hgt

    return dsp_wdh, dsp_hgt

import os
import shutil
import warnings
from pathlib import Path

import cv2

from natsort import natsorted

import numpy as np

from pims import Frame, ND2Reader_SDK as ND2_Reader


def load_nd2_imgs(nd2, axs_config):
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
                'img_name'] = Path(f).suffix, f, Path(f).name
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

    height, width, layers = imgs[0].shape
    four_cc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv2.VideoWriter(output_path, four_cc, fps, (width, height))

    for img in imgs:
        out.write(img)

    # Release everything if job is finished
    out.release()
    cv2.destroyAllWindows()


def apply_metadata(img1, img2):
    img1 = Frame(img1)
    img1.metadata = img2.metadata

    return img1

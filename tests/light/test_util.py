# Copyright (c) 2021 Alphons Gwatimba
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import json
import os

import cv2

import numpy as np

from pims import Frame

from rainbow.optical_flow.optical_flow import OPTICAL_FLOW_FILENAME
from rainbow.util import (apply_metadata, comb_imgs, load_optical_flow,
                          load_std_imgs, save_img_ser, save_img_ser_metadata,
                          save_optical_flow, video_reshape)

from tests import IMG_SER_DIR, VID_PATH


def test_comb_imgs():
    img1, img2 = np.array([[1, 2], [3, 4]]), np.array([[5, 6], [7, 8]])
    img1, img2 = Frame(img1), Frame(img2)
    assert np.array_equal(comb_imgs(img1, img2), np.array([[1, 2, 5, 6],
                                                           [3, 4, 7, 8]]))


def test_save_img_ser_without_metadata_name(tmpdir):
    imgs = load_std_imgs(IMG_SER_DIR)
    save_img_ser(imgs, tmpdir, False)
    saved_imgs = next(os.walk(tmpdir))[2]
    assert len(saved_imgs) == 3
    for i, saved_img in enumerate(saved_imgs):
        assert saved_img == f'Image_{i}.png'
        assert cv2.imread(os.path.join(tmpdir, saved_img)) is not None


def test_save_img_ser_with_metadata_name(tmpdir):
    imgs = load_std_imgs(IMG_SER_DIR)
    save_img_ser(imgs, tmpdir)
    saved_imgs = next(os.walk(tmpdir))[2]
    assert len(saved_imgs) == 3
    for i, saved_img in enumerate(saved_imgs, start=1):
        assert saved_img == f'test_frame_{i}.png'
        assert cv2.imread(os.path.join(tmpdir, saved_img)) is not None


def test_save_optical_flow(tmpdir):
    preds = np.ones((10, 10, 2))
    save_optical_flow(preds, tmpdir)
    assert next(os.walk(tmpdir))[2][0] == OPTICAL_FLOW_FILENAME


def test_load_optical_flow(tmpdir):
    preds = np.ones((10, 10, 2))
    save_optical_flow(preds, tmpdir)
    saved_preds = os.path.join(tmpdir, next(os.walk(tmpdir))[2][0])
    assert np.array_equal(preds, load_optical_flow(saved_preds))


def test_apply_metadata():
    img1 = np.ones((10, 10, 3))
    _, img2, _ = load_std_imgs(IMG_SER_DIR)
    img1 = apply_metadata(img1, img2)
    assert img1.metadata == img2.metadata


def test_save_img_ser_metadata(tmpdir):
    imgs = load_std_imgs(IMG_SER_DIR)
    save_img_ser_metadata(imgs, tmpdir)
    saved_metadata = os.path.join(tmpdir, next(os.walk(tmpdir))[2][0])
    with open(saved_metadata) as f:
        assert len(json.load(f)) != 0


def test_video_reshape():
    assert video_reshape(VID_PATH, 128) == (128, 54)

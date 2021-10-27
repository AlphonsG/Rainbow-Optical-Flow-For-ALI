# Copyright (c) 2021 Alphons Gwatimba
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import os
from pathlib import Path

import pytest

from rainbow.util import VID_FILE_EXT, load_nd2_imgs, load_std_imgs, save_video

from tests import IMG_SER_DIR, ND2_PATH


@pytest.fixture
def axs_config():
    return {'iter_axs': ['v', 't'],
            'bdl_axs': ['y', 'x'],
            'naming_axs': 'v'
            }


def test_load_std_imgs(tmpdir):
    imgs = load_std_imgs(IMG_SER_DIR, 1)
    assert len(imgs) == 3
    for i, img in enumerate(imgs, start=1):
        assert str(i) in img.metadata['img_name']
        assert img.metadata['mpp'] == 1

    assert len(load_std_imgs('')) == 0
    assert len(load_std_imgs(tmpdir)) == 0


def test_load_nd2_imgs(axs_config):
    imgs = load_nd2_imgs(ND2_PATH, axs_config)
    assert len(imgs) != 0  # TODO specfic
    assert len(imgs[0]) != 0
    assert imgs[3][0].shape == (1024, 1280, 3)
    assert len(imgs[0][0].metadata) != 0
    assert imgs[6][0].metadata['type'] == '.nd2'
    assert imgs[9][0].metadata['path'] == ND2_PATH
    assert imgs[12][0].metadata['img_name'] == 'Image_0.png'


def test_save_video(tmpdir):
    assert save_video(IMG_SER_DIR, os.path.join(tmpdir, 'test_video'))
    video = os.path.join(tmpdir, next(os.walk(tmpdir))[2][0])
    assert Path(video).suffix == VID_FILE_EXT

# Copyright (c) 2021 Alphons Gwatimba
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import os
import warnings

import numpy as np

import pytest

from rainbow.optical_flow.model_factory import ModelFactory
from rainbow.optical_flow.optical_flow import (OPTICAL_FLOW_FILENAME,
                                               compute_optical_flow)
from rainbow.util import load_std_imgs

from tests import IMG_SER_DIR


@pytest.fixture
def gma_cfg():
    return {'model': 'gma-sintel.pth',
            'model_name': 'GMA',
            'num_heads': 1,
            'position_only': False,
            'position_and_content': False,
            'mixed_precision': False,
            'device': 'cpu'
            }


def test_gma_predict(gma_cfg):
    model_factory = ModelFactory()
    model = model_factory.get_model('gma', gma_cfg, True)
    imgs = load_std_imgs(IMG_SER_DIR)

    preds = model.predict(imgs)
    assert len(preds) == 2
    for pred in preds:
        assert pred.shape[2] == 2
        assert not np.isnan(preds).any()


def test_compute_optical_flow(tmpdir, gma_cfg):
    imgs = load_std_imgs(IMG_SER_DIR)

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=UserWarning)
        compute_optical_flow(imgs, tmpdir, 'gma', gma_cfg,
                             overwrite_flow=False)
    saved_flow1 = [os.path.join(tmpdir, f) for f in next(os.walk(tmpdir))[2] if
                   f == OPTICAL_FLOW_FILENAME]
    assert len(saved_flow1) == 1
    saved_flow1_mtime = os.path.getmtime(saved_flow1[0])
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=UserWarning)
        compute_optical_flow(imgs, tmpdir, 'gma', gma_cfg,
                             overwrite_flow=False)
    saved_flow2 = [os.path.join(tmpdir, f) for f in next(os.walk(tmpdir))[2] if
                   f == OPTICAL_FLOW_FILENAME]
    assert len(saved_flow2) == 1
    assert saved_flow1_mtime == os.path.getmtime(saved_flow2[0])

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=UserWarning)
        compute_optical_flow(imgs, tmpdir, 'gma', gma_cfg,
                             overwrite_flow=True)
    saved_flow3 = [os.path.join(tmpdir, f) for f in next(os.walk(tmpdir))[2] if
                   f == OPTICAL_FLOW_FILENAME]
    assert len(saved_flow3) == 1
    assert saved_flow1_mtime != os.path.getmtime(saved_flow3[0])

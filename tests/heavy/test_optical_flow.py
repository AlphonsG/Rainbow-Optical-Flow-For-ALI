# Copyright (c) 2021 Alphons Gwatimba
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import os

import numpy as np

import pytest

from rainbow.optical_flow.model_factory import ModelFactory
from rainbow.optical_flow.optical_flow import (load_optical_flow,
                                               save_optical_flow,
                                               OPTICAL_FLOW_FILENAME)
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
    model = model_factory.get_model('gma', gma_cfg)
    model.load()

    imgs = load_std_imgs(IMG_SER_DIR)
    imgs = model.prepare(imgs)
    preds = model.run(imgs)

    assert preds.shape[0] == 2
    for i in range(0, preds.shape[0]):
        assert preds[i, ...].shape[0] > 0
        assert preds[i, ...].shape[1] > 0
        assert preds[i, ...].shape[2] == 2
        assert not np.isnan(preds).any()


def test_save_optical_flow(tmpdir):
    preds = np.ones((10, 10, 2))
    save_optical_flow(preds, tmpdir)
    assert next(os.walk(tmpdir))[2][0] == OPTICAL_FLOW_FILENAME


def test_load_optical_flow(tmpdir):
    preds = np.ones((10, 10, 2))
    save_optical_flow(preds, tmpdir)
    saved_preds = os.path.join(tmpdir, next(os.walk(tmpdir))[2][0])
    assert np.array_equal(preds, load_optical_flow(saved_preds))

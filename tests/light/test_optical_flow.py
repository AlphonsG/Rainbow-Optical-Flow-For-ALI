# Copyright (c) 2021 Alphons Gwatimba
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import numpy as np

import pytest

from rainbow.optical_flow.base_model import BaseModel
from rainbow.optical_flow.model_factory import ModelFactory
from rainbow.optical_flow.optical_flow import flow_to_img
from rainbow.util import load_std_imgs

from tests import IMG_SER_DIR


class TestModel(BaseModel):
    def __init__(self):
        pass


@pytest.fixture
def test_model():
    return TestModel()


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


def test_model_factory():
    model_factory = ModelFactory()
    with pytest.raises(ValueError):
        model_factory.get_model('', None, False)


def test_gma_instantiation(gma_cfg):
    model_factory = ModelFactory()
    model1 = model_factory.get_model('gma', gma_cfg, True)
    assert model1 is not None
    with pytest.raises(ValueError):
        model_factory.get_model('gma', gma_cfg, False)

    model2 = model_factory.get_model('gma', gma_cfg, True)
    assert model1 is model2


def test_base_model_get_img_pairs(test_model):
    imgs = load_std_imgs(IMG_SER_DIR)
    img_pairs = test_model.get_img_pairs(imgs)
    assert len(img_pairs) == 2
    assert np.array_equal(img_pairs[0][0], imgs[0])
    assert np.array_equal(img_pairs[0][1], imgs[1])
    assert np.array_equal(img_pairs[1][0], imgs[1])
    assert np.array_equal(img_pairs[1][1], imgs[2])


def test_flow_to_img():
    flow = np.ones((10, 10, 2))
    assert flow_to_img(flow).shape == (10, 10, 3)
    assert not np.isnan(flow).any()

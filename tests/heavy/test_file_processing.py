# Copyright (c) 2021 Alphons Gwatimba
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import os
import shutil
from pathlib import Path

import pytest

from rainbow.file_processing import get_output_dir, process_files
from rainbow.util import load_nd2_imgs, load_std_imgs

from tests import IMG_SER_DIR, ND2_PATH


@pytest.fixture
def nd2_config():
    return {'nd2': {'iter_axs': ['z', 'm', 't'],
                    'bdl_axs': ['y', 'x'],
                    'naming_axs': 'm'
                    }
            }


@pytest.fixture
def img_dir(tmpdir):
    shutil.copytree(IMG_SER_DIR, os.path.join(tmpdir, 'test_img_dir'))
    return os.path.join(tmpdir, 'test_img_dir')


@pytest.fixture
def config():
    return {'report_path': 'report.ipynb',
            'nd2': {'iter_axs': ['z', 'm', 't'],
                    'bdl_axs': ['y', 'x'],
                    'naming_axs': 'm'
                    },
            'mpp': 0.31302569743655434,
            'opt_flow_model': 'gma',
            'gma': {'model': 'gma-sintel.pth',
                    'model_name': 'GMA',
                    'num_heads': 1,
                    'position_only': False,
                    'position_and_content': False,
                    'mixed_precision': False,
                    'device': 'cpu'
                    }
            }


@pytest.fixture
def img_seqs(tmpdir):
    shutil.copytree(IMG_SER_DIR, os.path.join(tmpdir, 'test_img_dir'))
    yield os.path.join(tmpdir, 'test_img_dir')

    root_dir = os.path.dirname(ND2_PATH)
    tmp_dirs = next(os.walk(root_dir))[1]
    for tmp_dir in tmp_dirs:
        shutil.rmtree(os.path.join(root_dir, tmp_dir))


def test_process_files(img_dir, config):
    num_wrkrs, subdirs, overwrite_flow = 1, False, True
    process_files(img_dir, config, num_wrkrs, subdirs, overwrite_flow)
    output_dir = [os.path.join(img_dir, d) for d in next(os.walk(
                  img_dir))[1]][0]
    _, dirs, files = next(os.walk(output_dir))
    assert len(dirs) != 0
    assert len(files) != 0
    file_exts = [Path(f).suffix for f in files]
    assert '.html' in file_exts
    assert '.ipynb' in file_exts


def test_get_output_dir(img_seqs, nd2_config):
    imgs = load_std_imgs(img_seqs)
    output_dir = get_output_dir(imgs, nd2_config)
    os.mkdir(output_dir)
    assert len(next(os.walk(img_seqs))[1]) == 1

    imgs = load_nd2_imgs(ND2_PATH, nd2_config['nd2'])
    output_dir = get_output_dir(imgs[0], nd2_config)
    os.mkdir(output_dir)
    assert len(next(os.walk(img_seqs))[1]) == 1

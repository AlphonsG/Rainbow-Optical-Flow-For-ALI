# Copyright (c) 2021 Alphons Gwatimba
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import os
import shutil
import warnings
from pathlib import Path

import pytest

from rainbow.file_processing import process_files
from rainbow.optical_flow.optical_flow import OPTICAL_FLOW_FILENAME

from tests import IMG_SER_DIR, ND2_PATH


@pytest.fixture
def nd2_config():
    return {'nd2': {'iter_axs': ['v', 't'],
                    'bdl_axs': ['y', 'x'],
                    'naming_axs': 'v'
                    }
            }


@pytest.fixture
def img_dir(tmpdir):
    shutil.copytree(IMG_SER_DIR, os.path.join(tmpdir, 'test_img_dir'))
    return os.path.join(tmpdir, 'test_img_dir')


@pytest.fixture
def config():
    return {'report_path': 'report.ipynb',
            'nd2': {'iter_axs': ['v', 't'],
                    'bdl_axs': ['y', 'x'],
                    'naming_axs': 'v'
                    },
            'mpp': 0.31302569743655434,
            'optical_flow_model': 'gma',
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


def test_process_files(img_dir, config):  # TODO test subdirs
    num_wrkrs, use_existing_flow = 1, True
    process_files(img_dir, config, num_wrkrs,
                  use_existing_flow=use_existing_flow)
    assert len(next(os.walk(img_dir))[1]) != 0  # output dirs created
    output_dir = [os.path.join(img_dir, d) for d in next(os.walk(
        img_dir))[1]][0]
    _, dirs, files = next(os.walk(output_dir))
    assert len(dirs) != 0
    assert len(files) != 0
    file_exts = [Path(f).suffix for f in files]
    assert '.html' in file_exts
    assert '.ipynb' in file_exts
    saved_flow1 = [os.path.join(output_dir, f) for f in next(os.walk(
        output_dir))[2] if f == OPTICAL_FLOW_FILENAME]
    assert len(saved_flow1) == 1
    saved_flow1_mtime = os.path.getmtime(saved_flow1[0])

    analyze_data = False
    num_wrkrs = 2
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=UserWarning)
        process_files(img_dir, config, num_wrkrs,
                      use_existing_flow=use_existing_flow,
                      analyze_data=analyze_data)
    saved_flow2 = [os.path.join(output_dir, f) for f in next(os.walk(
        output_dir))[2] if f == OPTICAL_FLOW_FILENAME]
    assert len(saved_flow2) == 1
    assert saved_flow1_mtime == os.path.getmtime(saved_flow2[0])

    use_existing_flow = False
    num_wrkrs = 0
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=UserWarning)
        process_files(img_dir, config, num_wrkrs,
                      use_existing_flow=use_existing_flow,
                      analyze_data=analyze_data)
    saved_flow3 = [os.path.join(output_dir, f) for f in next(os.walk(
        output_dir))[2] if f == OPTICAL_FLOW_FILENAME]
    assert len(saved_flow3) == 1
    assert saved_flow1_mtime != os.path.getmtime(saved_flow3[0])

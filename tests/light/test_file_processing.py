# Copyright (c) 2021 Alphons Gwatimba
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import os
import shutil

import pytest

from rainbow.file_processing import skip_opt_flow
from rainbow.optical_flow.optical_flow import OPTICAL_FLOW_FILENAME

from tests import IMG_SER_DIR


@pytest.fixture
def img_dir(tmpdir):
    shutil.copytree(IMG_SER_DIR, os.path.join(tmpdir, 'test_img_dir'))
    return os.path.join(tmpdir, 'test_img_dir')


def test_skip_opt_flow(tmpdir):
    assert not skip_opt_flow(tmpdir, True)
    assert not skip_opt_flow(tmpdir, False)
    tmpdir.join(OPTICAL_FLOW_FILENAME).write('content')
    assert not skip_opt_flow(tmpdir, True)
    assert skip_opt_flow(tmpdir, False)

# Copyright (c) 2021 Alphons Gwatimba
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import os
from pathlib import Path

import numpy as np

from rainbow.data_analysis import (gen_report, save_heatmaps, save_polar_plots,
                                   save_quiver_plots)

from tests import NOTEBOOK_PATH


def test_save_heatmaps(tmpdir):
    preds = [np.random.uniform(low=-10, high=10, size=(5, 5, 2)),
             np.random.uniform(low=-10, high=10, size=(5, 5, 2))]
    save_heatmaps(preds, tmpdir)
    files = next(os.walk(tmpdir))[2]
    files.sort()
    assert files[0] == 'Image_0.png'
    assert files[1] == 'Image_1.png'


def test_save_quiver_plots(tmpdir):
    preds = [np.random.uniform(low=-10, high=10, size=(5, 5, 2)),
             np.random.uniform(low=-10, high=10, size=(5, 5, 2))]
    save_quiver_plots(preds, tmpdir)
    files = next(os.walk(tmpdir))[2]
    files.sort()
    assert files[0] == 'Image_0.png'
    assert files[1] == 'Image_1.png'


def test_save_polar_plots(tmpdir):
    preds = [np.random.uniform(low=-10, high=10, size=(5, 5, 2)),
             np.random.uniform(low=-10, high=10, size=(5, 5, 2))]
    save_polar_plots(preds, tmpdir)
    files = next(os.walk(tmpdir))[2]
    files.sort()
    assert files[0] == 'Image_0.png'
    assert files[1] == 'Image_1.png'


def test_gen_report(tmpdir):
    gen_report(tmpdir, NOTEBOOK_PATH)
    files = next(os.walk(tmpdir))[2]
    files.sort(key=lambda x: Path(x).suffix)
    assert files[0] == f'{Path(NOTEBOOK_PATH).stem}.html'
    assert files[1] == Path(NOTEBOOK_PATH).name

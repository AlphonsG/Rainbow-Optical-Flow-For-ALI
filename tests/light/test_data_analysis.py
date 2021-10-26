# Copyright (c) 2021 Alphons Gwatimba
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import os
from collections import defaultdict
from pathlib import Path

import numpy as np

from rainbow.data_analysis import (gen_base_metrics, gen_stats, save_html,
                                   save_stats)
from rainbow.util import load_std_imgs

from tests import IMG_SER_DIR, NOTEBOOK_PATH


def test_save_html(tmpdir):
    save_html(tmpdir, NOTEBOOK_PATH)
    assert next(os.walk(tmpdir))[2][0] == f'{Path(NOTEBOOK_PATH).stem}.html'


def test_gen_stats():
    vals = np.random.randint(0, 100, 5).tolist()
    frame = 0
    stats = gen_stats(vals, frame)
    assert len(stats) != 0


def test_save_stats(tmpdir):
    vals1 = np.random.randint(0, 100, 5).tolist()
    vals2 = np.random.randint(0, 100, 5).tolist()
    stats = [gen_stats(vals1, 1), gen_stats(vals2, 2)]
    save_stats(stats, os.path.join(tmpdir, 'test.csv'), 'unit')
    assert next(os.walk(tmpdir))[2][0] == 'test.csv'


def test_gen_base_metrics():
    data = defaultdict(list)
    imgs = load_std_imgs(IMG_SER_DIR, 1)
    data['raw_imgs'] = imgs
    preds = [np.random.uniform(low=-10, high=10, size=(5, 5, 2)),
             np.random.uniform(low=-10, high=10, size=(5, 5, 2))]
    data['preds'] = preds
    gen_base_metrics(data)
    assert len(data) > 2
    for vals in data.values():
        assert len(vals) != 0

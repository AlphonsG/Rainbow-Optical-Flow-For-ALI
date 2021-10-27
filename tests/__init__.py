# Copyright (c) 2021 Alphons Gwatimba
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                '..')))

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
IMG_SER_DIR = os.path.join(DATA_DIR, 'test_image_series')
VID_PATH = os.path.join(DATA_DIR, 'test_video.gif')
ND2_PATH = os.path.join(DATA_DIR, 'test_nd2', 'test_nd2.nd2')
NOTEBOOK_PATH = os.path.join(DATA_DIR, 'test_notebook.ipynb')

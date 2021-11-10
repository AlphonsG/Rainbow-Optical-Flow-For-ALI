# Copyright (c) 2021 Alphons Gwatimba
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import os
from argparse import ArgumentParser
from pathlib import Path

from astropy import units as u
from astropy.stats import circcorrcoef

import cv2

import numpy as np

FLOW_FILE_EXT = '.npy'


def process_args():
    parser = ArgumentParser(description='Compares the optical flow between 2 '
                            'image sequences by computing the circular '
                            'correlation coefficient between the circular '
                            'data in all pairs of frames.')
    parser.add_argument('input_dir1', type=str, help='path to folder '
                        'containing optical flow file')
    parser.add_argument('input_dir2', type=str, help='path to folder '
                        'containing optical flow file')
    args = parser.parse_args()

    return args


def main():
    args = process_args()
    for input_dir in [args.input_dir1, args.input_dir2]:
        assert os.path.isdir(input_dir), (f'Input directory ({input_dir}) is '
                                          'not a valid directory.')

    compare_optical_flow(args.input_dir1, args.input_dir2)


def compare_optical_flow(input_dir1, input_dir2):
    print(f'Processing image sequences \'{input_dir1}\' and \'{input_dir2}\'.')
    flow_files = []
    for input_dir in [input_dir1, input_dir2]:
        flow_files += [os.path.join(input_dir, f) for f in next(os.walk(
            input_dir))[2] if Path(f).suffix == FLOW_FILE_EXT]
    assert len(flow_files) == 2, ('Input directories do not contain one '
                                  f'optical flow file ({FLOW_FILE_EXT}) each.')

    flows = [np.load(f) for f in flow_files]
    assert len(flows[0]) == len(flows[1]), ('Corresponding image sequences '
                                            'are not the same length.')

    print('Circular correlation coefficients between corresponding frames of '
          'input image sequences:')
    for i, (flow1, flow2) in enumerate(zip(flows[0], flows[1]), start=1):
        angs = [cv2.cartToPolar(fw[..., 0].astype(float), fw[..., 1].astype(
            float), angleInDegrees=1)[1] * u.deg for fw in [flow1, flow2]]

        print(f'Frame {i}: {round(float(circcorrcoef(angs[0], angs[1])), 3)}')


if __name__ == '__main__':
    main()

import os
import sys
from argparse import ArgumentParser
from time import time

from rainbow.file_processing import process_files

import yaml


def process_args():
    parser = ArgumentParser(description="""
                            RAINBOW: Automated air liquid
                            interface cell culture analysis using
                            deep optical flow. This tool will process
                            time lapse image sequences from .nd2 files
                            or standard image files such as .png
                            files. Rainbow processes all
                            compatible files in the provided root
                            directory and in every
                            subfolder by default. The results of
                            the analysis are placed in a
                            folder that is created in the
                            same directory as the analyzed
                            image sequence. The results folder
                            name begins with the type of image
                            sequence analyzed in brackets and is
                            named to easily identify the original
                            sequence. Rainbow can utilize a GPU
                            to compute optical flow and can
                            analyze multiple folders in parallel""")
    parser.add_argument('root_dir', type=str, help='path to root directory '
                        'to begin searching for compatible files to process '
                        'in')
    parser.add_argument('config', type=str, help='path to YAML configuration '
                        'file')
    parser.add_argument('--num-workers', type=int, default=-1, help='maximum '
                        'number of CPUs to utilize for parallel analysis '
                        '(default (-1) uses all CPUs)')
    parser.add_argument('--non-recursive', dest='recursive',
                        action='store_false', help='disable processing of '
                        'compatible files in root directory subfolders')
    parser.add_argument('--debug', action='store_true',
                        help='run in debug mode i.e. single process')
    args = parser.parse_args()

    return args


def main(args=None):
    args = process_args()
    assert os.path.isdir(args.root_dir), ('Invalid root directory path '
                                          'provided.')
    assert os.path.isfile(args.config), 'Invalid config file path provided.'
    assert args.num_workers == -1 or args.num_workers > 0, ('Invalid CPU '
                                                            'count provided.')

    with open(args.config) as f:
        config = yaml.safe_load(f)

    start = time()
    process_files(args.root_dir, config, args.num_workers, args.recursive,
                  args.debug)
    end = time()
    runtime = int(end - start)
    print('Finished in {} seconds!'.format(runtime))

    return 0


if __name__ == "__main__":
    __spec__ = None  # pdb multiprocessing support
    sys.exit(main())

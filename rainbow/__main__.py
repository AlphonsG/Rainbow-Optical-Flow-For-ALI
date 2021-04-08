import os
import sys
from argparse import ArgumentParser
from time import time

from rainbow.file_processing import process_files

import yaml


def process_args():
    parser = ArgumentParser(description='Automated air liquid interface cell '
                                        'culture analysis using deep optical '
                                        'flow.')
    parser.add_argument('root_dir', type=str, help=('root directory to begin '
                        'performing analysis in'))
    parser.add_argument('config', type=str, help='YAML configuration file')
    parser.add_argument('--num-workers', type=int, default=-1, help='maximum '
                        'number of CPUs to utilize (default (-1) uses all '
                        'CPUs)')
    parser.add_argument('--non-recursive', dest='recursive',
                        action='store_false', help='do not process compatible '
                        'files in root directory subfolders')
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
    process_files(args.root_dir, config, args.num_workers, args.recursive)
    end = time()
    runtime = int(end - start)
    print('Finished in {} seconds!'.format(runtime))

    return 0


if __name__ == "__main__":
    __spec__ = None  # pdb multiprocessing support
    sys.exit(main())

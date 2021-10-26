import os
from argparse import ArgumentParser

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
                            directory. The results of
                            the analysis are placed in a
                            folder that is created in the
                            same directory as the analyzed
                            image sequence. The results folder
                            name begins with the type of image
                            sequence analyzed in brackets and is
                            named to easily identify the original
                            sequence. Rainbow can utilize a GPU
                            to compute optical flow and can
                            analyze multiple folders in parallel.""")
    parser.add_argument('root_dir', type=str, help='path to root directory '
                        'to begin searching for compatible files to process '
                        'in')
    parser.add_argument('config', type=str, help='path to YAML configuration '
                        'file')
    parser.add_argument('--num-workers', type=int, help='maximum '
                        'number of workers to use for parallel analysis '
                        '(default equals CPU core count)')
    parser.add_argument('--subdirs', help='process files in root directory '
                        'subfolders instead', action='store_true')
    parser.add_argument('--overwrite-flow', action='store_true',
                        help='recompute optical flow even if preexisting '
                             'optical flow file exists for an image series')
    args = parser.parse_args()

    return args


def main():
    args = process_args()  # check checkpoint path
    assert os.path.isdir(args.root_dir), ('Invalid root directory path '
                                          'provided.')
    assert os.path.isfile(args.config), 'Invalid config file path provided.'
    assert args.num_workers is None or args.num_workers > 0, (
        'Invalid number of workers provided.')

    with open(args.config) as f:
        config = yaml.safe_load(f)

    process_files(args.root_dir, config, args.num_workers, args.subdirs,
                  args.overwrite_flow)

    return 0


if __name__ == "__main__":
    __spec__ = None  # pdb multiprocessing support
    main()

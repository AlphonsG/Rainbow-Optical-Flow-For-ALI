import os
import sys

from gooey import Gooey, GooeyParser

from rainbow.file_processing import process_files

# check if pytorch is installed
try:
    import torch
except ModuleNotFoundError:
    msg = ('Rainbow cannot run because PyTorch is currently '
           'not installed. Please install Pytorch by following step 4 of '
           'Rainbow\'s installation instructions: https://github.com/AlphonsG/'
           'Rainbow-Optical-Flow-For-ALI#installation-.')
    print(msg)
    exit(1)

import yaml


if len(sys.argv) >= 2 and '--ignore-gooey' not in sys.argv:
    sys.argv.append('--ignore-gooey')


@Gooey(hide_progress_msg=True)
def process_args():
    parser = GooeyParser(description='Automated air liquid interface cell '
                         'culture analysis using deep optical flow.')
    parser.add_argument('root_dir', type=str, help='path to root directory '
                        'to begin searching for image sequences to process '
                        'in', widget='DirChooser')
    parser.add_argument('config', type=str, help='path to YAML configuration '
                        'file', widget='FileChooser')
    parser.add_argument('--num-workers', type=int, default=0,
                        help='maximum number of workers to utilize in '
                        'parallel during execution (leave as default value '
                        'to automatically determine the number of workers '
                        'that will utilize all available CPU cores)',
                        widget='IntegerField', gooey_options={'min': 0})
    parser.add_argument('--sub-dirs', help='process files in root directory '
                        'subfolders instead of top level directory',
                        action='store_true')
    parser.add_argument('--use-existing-flow', action='store_true',
                        help='recompute optical flow even if preexisting '
                             'optical flow file is found for an image '
                             'sequence')
    parser.add_argument('--cleanup-output-dirs', action='store_true',
                        help='remove all existing files and folders from '
                        'output directories before saving new data')
    parser.add_argument('--analyze-data', action='store_true',
                        help='perform data analysis')
    parser.add_argument('--max-num-parl-preds', type=int, default=1,
                        help='the maximum number of image sequences that can '
                             'be fed to the optical flow model '
                             'simultaneously (Note: too high a value may '
                             'result in errors from over-consumption of '
                             'system/GPU memory)', widget='IntegerField',
                             gooey_options={'min': 1})

    args = parser.parse_args()

    return args


def main():
    args = process_args()
    assert os.path.isdir(args.root_dir), ('Invalid root directory path '
                                          'provided.')
    assert os.path.isfile(args.config), 'Invalid config file path provided.'
    assert args.num_workers is None or args.num_workers >= 0, (
        'Invalid number of workers provided.')

    with open(args.config) as f:
        config = yaml.safe_load(f)

    process_files(args.root_dir, config, args.num_workers, args.sub_dirs,
                  args.use_existing_flow, args.cleanup_output_dirs,
                  args.analyze_data, args.max_num_parl_preds)

    return 0


if __name__ == "__main__":
    main()

import os
import sys

from gooey import Gooey, GooeyParser

from rainbow.file_processing import process_files

import yaml


if len(sys.argv) >= 2 and '--ignore-gooey' not in sys.argv:
    sys.argv.append('--ignore-gooey')


@Gooey(hide_progress_msg=True)
def process_args():
    parser = GooeyParser(description='Automated air liquid interface cell '
                         'culture analysis using deep optical flow.')
    parser.add_argument('root_dir', type=str, help='Path to root directory '
                        'to begin searching for image sequences to process '
                        'in', widget='DirChooser')
    parser.add_argument('config', type=str, help='Path to YAML configuration '
                        'file', widget='FileChooser')
    parser.add_argument('--num-workers', type=int, help='Maximum '
                        'number of workers to use for parallel analysis '
                        '(default number equals CPU core count)',
                        widget='IntegerField', gooey_options={'min': 1})
    parser.add_argument('--subdirs', help='Process files in root directory '
                        'subfolders instead', action='store_true')
    parser.add_argument('--overwrite-flow', action='store_true',
                        help='Recompute optical flow even if preexisting '
                             'optical flow file is found for an image series')
    args = parser.parse_args()

    return args


def main():
    args = process_args()
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

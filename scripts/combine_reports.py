import os
from argparse import ArgumentParser

REPORT_FILE_EXT = '.html'
COMBINED_REPORT_PREFIX = 'combined_'


def process_args():
    parser = ArgumentParser(description='Combines multiple analysis reports '
                            'into one report.')
    parser.add_argument('root_dir', type=str, help='path to folder to begin '
                        'recursively searching for analysis reports in')
    parser.add_argument('report_name', type=str, help='name of analysis '
                        'reports')
    parser.add_argument('output_dir', type=str, help='path to output '
                        'directory')
    args = parser.parse_args()

    return args


def main():
    args = process_args()
    assert os.path.isdir(args.root_dir) and os.path.isdir(args.output_dir), (
        'Root and/or output directory is not a valid directory.')

    process(args.root_dir, args.report_name, args.output_dir)

    return 0


def process(root_dir, report_name, output_dir):
    report_filename = report_name + REPORT_FILE_EXT
    reports = []
    for curr_dir, dirs, files in os.walk(root_dir):
        if report_filename in files:
            reports.append(os.path.join(curr_dir, report_filename))

    if len(reports) != 0:
        with open(os.path.join(output_dir,
                  COMBINED_REPORT_PREFIX + report_filename), 'w',
                  encoding='utf-8') as f_out:
            for report in reports:
                with open(report, encoding='utf-8') as f_in:
                    for line in f_in:
                        f_out.write(line)

    return 0


if __name__ == '__main__':
    main()

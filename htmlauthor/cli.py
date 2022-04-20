import argparse
import sys
from cli_utils import determine_file_or_url, process_file, process_url

file_func = {
    'isURL': process_url,
    'isFile': process_file
}


def process_arge(args):
    file_type = determine_file_or_url(args.p)
    if file_type is not None:
        return file_func[file_type](args.p)
    else:
        print('Invalid URL or filepath {}'.format(args.p))
    return None


def main():
    args = parse_args()
    author = process_arge(args)
    print(author)


def parse_args():
    parser = argparse.ArgumentParser(description='Command-line interface for html-author')
    parser.add_argument('-p', type=str, help='Path or URL for extraction')
    parser.add_argument('-b', type=bool, default=True, help='Whether uses baseline to improve the recall rate.')
    # parser.print_help()
    return parser.parse_args()


if __name__ == '__main__':
    main()

import argparse
import logging

from subseek import __version__
from subseek.core import SubSeek, DownloadFirstHandler

def parse_args(argv=None):
    parser = argparse.ArgumentParser(version=__version__)
    parser.add_argument('filepaths', nargs='+')
    parser.add_argument('-l', '--language', default='en')
    return parser.parse_args(argv)

def main(argv=None):
    logging.basicConfig()
    options = parse_args()
    subseek = SubSeek()

    handler = DownloadFirstHandler(subseek)
    handler.run(options.filepaths, options.language.split(','))

if __name__ == '__main__':
    main()

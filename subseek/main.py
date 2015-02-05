import argparse
import logging

from subseek import __version__, core

def parse_args(argv=None):
    parser = argparse.ArgumentParser(version=__version__)
    parser.add_argument('filepaths', nargs='+')
    parser.add_argument('-l', '--language', default='en')
    return parser.parse_args(argv)

def main(argv=None):
    logging.basicConfig()
    options = parse_args()
    subseek = core.SubSeek()

    subtitles = []
    for filepath in options.filepaths:
        subtitles.extend(subseek.search(filepath, options.language.split(',')))

    print subseek.download(subtitles[0])

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

# This file is part of subseek.
#
# subseek is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# subseek is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with subseek. If not, see <http://www.gnu.org/licenses/>.

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

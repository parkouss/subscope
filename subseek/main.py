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

from subseek import __version__, languages
from subseek.core import SubSeek, DownloadFirstHandler
from subseek.sources import SubSeekSource

LOG = logging.getLogger(__name__.split('.')[0])

class FinalAction(argparse.Action):
    help = None
    def __init__(self, option_strings, dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS):
        super(FinalAction, self).__init__(option_strings=option_strings,
                                          dest=dest, default=default,
                                          nargs=0, help=self.help)

    def __call__(self, parser, namespace, values, option_string=None):
        self.execute()
        parser.exit()

class ListSources(FinalAction):
    help = "list available subtitles sources and exit"
    def execute(self):
        for source_name in sorted(SubSeekSource.REGISTRY):
            print(" - %s" % source_name)

class ListLangs(FinalAction):
    help = ("list language codes (ISO 639-1 two chars sources) and exit."
            " Note that all these codes are not used by every sources.")
    def execute(self):
        langs = sorted(languages.LANGS.items(), key=lambda l: l[1])
        for code, desc in langs:
            print(" %s: %s" % (code, desc))

def parse_args(argv=None):
    parser = argparse.ArgumentParser(version=__version__)
    parser.add_argument('--log-level', default='info',
                        choices=('debug', 'info', 'warning', 'error'),
                        help="logging level. default to %(default)s")
    parser.add_argument('--sources', action=ListSources)
    parser.add_argument('--languages', action=ListLangs)
    parser.add_argument('-l', '--language', default='en')
    parser.add_argument('filepaths', nargs='+')
    return parser.parse_args(argv)

def main(argv=None):
    logging.basicConfig()
    options = parse_args()
    LOG.setLevel(getattr(logging, options.log_level.upper()))
    subseek = SubSeek()

    handler = DownloadFirstHandler(subseek)
    handler.run(options.filepaths, options.language.split(','))

if __name__ == '__main__':
    main()

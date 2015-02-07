# -*- coding: utf-8 -*-

# This file is part of telescope.
#
# telescope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# telescope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with telescope. If not, see <http://www.gnu.org/licenses/>.

import os
import argparse
import logging
from ConfigParser import ConfigParser

from telescope import __version__, languages
from telescope.core import Telescope, DownloadFirstHandler
from telescope.sources import TelescopeSource

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
        for source_name in sorted(TelescopeSource.REGISTRY):
            print(" - %s" % source_name)

class ListLangs(FinalAction):
    help = ("list language codes (ISO 639-1 two chars sources) and exit."
            " Note that all these codes are not used by every sources.")
    def execute(self):
        langs = sorted(languages.LANGS.items(), key=lambda l: l[1])
        for code, desc in langs:
            print(" %s: %s" % (code, desc))

def parse_args(argv=None, **defaults):
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action="version", version=__version__)
    parser.add_argument('--log-level',
                        default=defaults.get('log-level', 'info'),
                        choices=('debug', 'info', 'warning', 'error'),
                        help="logging level. default to %(default)s")
    parser.add_argument('--sources', action=ListSources)
    parser.add_argument('--languages', action=ListLangs)
    parser.add_argument('-l', '--language',
                        default=defaults.get('language', 'en'))
    parser.add_argument('filepaths', nargs='+')
    return parser.parse_args(argv)

def read_conf(conf_file):
    defaults = {}
    if os.path.isfile(conf_file):
        print('Reading configuration file %s...' % conf_file)
        conf = ConfigParser()
        conf.read([conf_file])
        defaults = dict(conf.items('telescope'))
    return defaults

def main(argv=None):
    logging.basicConfig()

    defaults = read_conf(os.path.expanduser('~/.telescope.cfg'))

    options = parse_args(argv, **defaults)
    LOG.setLevel(getattr(logging, options.log_level.upper()))
    telescope = Telescope()

    handler = DownloadFirstHandler(telescope)
    handler.run(options.filepaths, options.language.split(','))

# -*- coding: utf-8 -*-

# This file is part of subscope.
#
# subscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# subscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with subscope. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import argparse
import logging
import requests
from requests.exceptions import RequestException
from ConfigParser import ConfigParser

from subscope import __version__, languages
from subscope.core import (Subscope, DownloadFirstHandler, 
                            DownloadInteractiveHandler)
from subscope.sources import SubscopeSource

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
        for source_name in sorted(SubscopeSource.REGISTRY):
            print(" - %s" % source_name)

class ListLangs(FinalAction):
    help = ("list language codes (ISO 639-1 two chars codes) and exit."
            " Note that all these codes are not used by every sources")
    def execute(self):
        langs = sorted(languages.LANGS.items(), key=lambda l: l[1])
        for code, desc in langs:
            print(" %s: %s" % (code, desc))

def parse_args(argv=None, **defaults):
    usage = "%(prog)s [options] filepath [filepath ...]"

    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('-v', '--version', action="version",
                        version=__version__)

    parser.add_argument('-l', '--language',
                        default=defaults.get('language', 'en'),
                        help=("comma separated list of desired langs for the"
                              " subtitles (ISO 639-1 two chars). Default to"
                              " %(default)s"))

    parser.add_argument('-f', '--force', action='store_true',
                        help=("force download of subtitle even if one"
                              " already exists"))

    parser.add_argument('-i', '--interactive', action='store_true',
                        help="interactive mode to download subtitles")

    parser.add_argument('-t', '--requests-timeout', type=float,
                        default=defaults.get('requests-timeout', '10.0'),
                        help=("set default timeout for requests in second."
                              " Default to %(default)s"))

    parser.add_argument('--log-level',
                        default=defaults.get('log-level', 'info'),
                        choices=('debug', 'info', 'warning', 'error'),
                        help="logging level. default to %(default)s")

    parser.add_argument('--sources', action=ListSources)
    parser.add_argument('--languages', action=ListLangs)
    parser.add_argument('filepaths', nargs='+',
                        help="path to your movie files")

    options = parser.parse_args(argv)
    options.requests_timeout = float(options.requests_timeout)
    options.language = options.language.replace(' ', '')
    return options

def read_conf(conf_file):
    defaults = {}
    if os.path.isfile(conf_file):
        print('Reading configuration file %s...' % conf_file)
        conf = ConfigParser()
        conf.read([conf_file])
        defaults = dict(conf.items('subscope'))
    return defaults

def set_requests_global_defaults(meth_name, **defaults):
    meth = getattr(requests, meth_name)
    def _meth(url, **kwargs):
        for k, v in defaults.iteritems():
            kwargs.setdefault(k, v)
        return meth(url, **kwargs)
    setattr(requests, meth_name, _meth)

def check_pypi_version():
    url = "https://pypi.python.org/pypi/subscope/json"
    try:
        pypi_version = requests.get(url).json()['info']['version']
    except (RequestException, KeyError, ValueError):
        LOG.critical("Unable to get latest version from pypi.")
        return
    if __version__ != pypi_version:
        LOG.warn("You are using subscope version %s, however version %s"
                 " is available.", __version__, pypi_version)
        LOG.warn("You should consider upgrading via the 'pip install"
                 " --upgrade subscope' command.")

def main(argv=None):
    logging.basicConfig()

    defaults = read_conf(os.path.expanduser('~/.subscope.cfg'))

    options = parse_args(argv, **defaults)
    LOG.setLevel(getattr(logging, options.log_level.upper()))

    check_pypi_version()

    subscope = Subscope()

    set_requests_global_defaults('get', timeout=options.requests_timeout)
    set_requests_global_defaults('post', timeout=options.requests_timeout)

    if options.interactive:
        handler_klass = DownloadInteractiveHandler
    else:
        handler_klass = DownloadFirstHandler
    handler = handler_klass(subscope, force=options.force)
    try:
        handler.run(options.filepaths, options.language.split(','))
    except KeyboardInterrupt:
        sys.exit("\nInterrupted.")

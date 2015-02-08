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

import unittest
import tempfile
import os
import requests

from subscope.tests import patch, Mock

from subscope import __version__
from subscope.main import (main, read_conf, set_requests_global_defaults,
                           check_pypi_version)

class TestMain(unittest.TestCase):
    @patch('sys.stderr')
    @patch('sys.stdout')
    @patch('subscope.main.DownloadFirstHandler')
    @patch('subscope.main.read_conf')
    @patch('subscope.main.check_pypi_version')
    def do_main(self, argv, check_pypi_version, read_conf,
                DownloadFirstHandler, stdout, stderr):
        read_conf.return_value = {}
        self.handler = Mock()
        DownloadFirstHandler.return_value = self.handler
        self.stdout = ''
        self.stderr = ''
        def do_write_stdout(txt):
            self.stdout += txt
        def do_write_stderr(txt):
            self.stderr += txt
        stdout.write.side_effect = do_write_stdout
        stderr.write.side_effect = do_write_stderr
        main(argv)

    def test_help(self):
        with self.assertRaises(SystemExit) as cm:
            self.do_main(['--help'])
        self.assertEquals(cm.exception.code, 0)
        self.assertIn('usage:', self.stdout)

    def test_version(self):
        with self.assertRaises(SystemExit) as cm:
            self.do_main(['--version'])
        self.assertEquals(cm.exception.code, 0)
        # this outputs on stderr on python2, stdout on python3 ... :)
        self.assertIn(__version__, self.stderr + self.stdout)

    def test_list_source(self):
        with self.assertRaises(SystemExit) as cm:
            self.do_main(['--source'])
        self.assertEquals(cm.exception.code, 0)
        self.assertIn('TheSubDB', self.stdout)

    def test_list_langs(self):
        with self.assertRaises(SystemExit) as cm:
            self.do_main(['--languages'])
        self.assertEquals(cm.exception.code, 0)
        self.assertIn(' fr: French', self.stdout)

    def test_no_langs_implies_en(self):
        self.do_main(['/my/movie'])
        self.handler.run.assert_called_with(['/my/movie'], ['en'])

    def test_std(self):
        self.do_main(['-l', 'fr,en', '/my/movie', '/my/movie2'])
        self.handler.run.assert_called_with(['/my/movie', '/my/movie2'], ['fr', 'en'])

class TestReadConf(unittest.TestCase):
    def test_simple(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"[subscope]\n"
                    b"language = fr,en\n")
        self.addCleanup(os.unlink, f.name)
        defaults = read_conf(f.name)
        self.assertEquals(defaults, {"language": "fr,en"})

class TestSetRequestsGlobalDefaults(unittest.TestCase):
    @patch('requests.get')
    def test_call_requests(self, get):
        set_requests_global_defaults('get', timeout=10.0)
        requests.get('http://foo')
        # default is applied
        get.assert_called_with('http://foo', timeout=10.0)
        # but can be overriden
        requests.get('http://foo', timeout=1)
        get.assert_called_with('http://foo', timeout=1)
        
class TestCheckPyPiVersion(unittest.TestCase):
    @patch('subscope.main.LOG')
    @patch('requests.get')
    def test_checkpypi_same(self, get, LOG):
        get.return_value = Mock(json= lambda: {'info': {'version': __version__}})
        check_pypi_version()
        self.assertFalse(LOG.warn.called)
        self.assertFalse(LOG.critical.called)

    @patch('subscope.main.LOG')
    @patch('requests.get')
    def test_checkpypi_new_release(self, get, LOG):
        get.return_value = Mock(json= lambda: {'info': {'version': '0.0'}})
        check_pypi_version()
        self.assertIn("You are using subscope version", LOG.warn.call_args_list[0][0][0])

    @patch('subscope.main.LOG')
    @patch('requests.get')
    def test_checkpypi_raise_exception(self, get, LOG):
        get.side_effect = KeyError
        check_pypi_version()
        self.assertIn("Unable to", LOG.critical.call_args_list[0][0][0])

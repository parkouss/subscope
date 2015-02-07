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

import unittest
import tempfile
import os

from subseek.tests import patch, Mock

from subseek import __version__
from subseek.main import main, read_conf

class TestMain(unittest.TestCase):
    @patch('sys.stderr')
    @patch('sys.stdout')
    @patch('subseek.main.DownloadFirstHandler')
    @patch('subseek.main.read_conf')
    def do_main(self, argv, read_conf, DownloadFirstHandler, stdout, stderr):
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
            f.write(b"[subseek]\n"
                    b"language = fr,en\n")
        self.addCleanup(os.unlink, f.name)
        defaults = read_conf(f.name)
        self.assertEquals(defaults, {"language": "fr,en"})

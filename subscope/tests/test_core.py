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
import shutil
import os

from subscope.tests import Mock, patch, PY2

from subscope.core import (Subscope, key_sub_by_langs, DownloadHandler,
                           subtitle_fname, DownloadFirstHandler,
                           DownloadInteractiveHandler)
from subscope.sources import SubscopeSource


class TestSubscope(unittest.TestCase):
    def setUp(self):
        self.subscope = Subscope()

    def test_sources_member_is_created(self):
        self.assertIsInstance(self.subscope.sources, dict)
        # sources are all present
        self.assertEquals(sorted(self.subscope.sources.keys()),
                          sorted(SubscopeSource.REGISTRY))

    def test_search(self):
        # mock the sources
        srcs = {}
        for name, search_return in [('src1', [{}]),
                                    ('src2', [{}, {}])]:
            src = Mock()
            src.name.return_value = name
            src.search.return_value = search_return
            srcs[name] = src
        self.subscope.sources = srcs

        result = self.subscope.search('/path/to/movie', ['en'])

        srcs['src1'].search.assert_called_with('/path/to/movie', ['en'])
        srcs['src2'].search.assert_called_with('/path/to/movie', ['en'])

        expected = [
            {'moviepath': '/path/to/movie', 'source': 'src2', 'ext': '.srt'},
            {'moviepath': '/path/to/movie', 'source': 'src2', 'ext': '.srt'},
            {'moviepath': '/path/to/movie', 'source': 'src1', 'ext': '.srt'}]
        self.assertEquals(sorted(sorted(r.items()) for r in result),
                          sorted(sorted(r.items()) for r in expected))

    def test_download(self):
        tempdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tempdir)

        def do_download(sub, stream):
            stream.write(b'this is my sub')

        self.subscope.sources = \
            {'test': Mock(download=Mock(side_effect=do_download))}

        path = os.path.join(tempdir, 'my-movie.avi')
        self.subscope.download({'source': 'test', 'moviepath': path,
                                'ext': '.srt'})

        with open(os.path.join(tempdir, 'my-movie.srt')) as f:
            self.assertEquals(f.read(), 'this is my sub')


class TestSubsByLangs(unittest.TestCase):
    def test_simple(self):
        subs = [
            {'lang': 'fr', 'source': '1'},
            {'lang': 'en', 'source': '1'},
            {'lang': 'fr', 'source': '2'},
        ]
        result = sorted(subs, key=key_sub_by_langs(['en', 'fr']))
        self.assertEquals(result, [
            {'lang': 'en', 'source': '1'},
            {'lang': 'fr', 'source': '1'},
            {'lang': 'fr', 'source': '2'},
        ])

    def test_with_unknown_lang(self):
        subs = [
            {'lang': 'fr', 'source': '1'},
            {'lang': 'en', 'source': '1'},
            {'lang': 'ru', 'source': '2'},
        ]
        result = sorted(subs, key=key_sub_by_langs(['en', 'fr']))
        self.assertEquals(result, [
            {'lang': 'en', 'source': '1'},
            {'lang': 'fr', 'source': '1'},
            {'lang': 'ru', 'source': '2'},
        ])


class TestDownloadHandler(unittest.TestCase):
    def setUp(self):
        self.subscope = Mock()
        self.handler = DownloadHandler(self.subscope)
        self.handler._handle = Mock()
        self.tempdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tempdir)

    def create_test_file(self, name):
        path = os.path.join(self.tempdir, name)
        with open(path, 'w') as f:
            f.write('something')
        return path

    def test_run(self):
        self.subscope.search.return_value = [1, 2]
        moviepath = self.create_test_file('mymovie.avi')
        self.handler.run([moviepath], ['en'])
        self.handler._handle.assert_called_with([1, 2], ['en'])

    @patch('subscope.core.LOG')
    def test_run_no_subtitles(self, LOG):
        self.subscope.search.return_value = []
        moviepath = self.create_test_file('mymovie.avi')
        self.handler.run([moviepath], ['en'])
        self.assertFalse(self.handler._handle.called)
        self.assertIn("Unable to find any subtitle",
                      LOG.warn.call_args_list[0][0][0])

    @patch('subscope.core.LOG')
    def test_run_path_does_not_exists(self, LOG):
        moviepath = 'somethingthatwontexists.avi'
        self.handler.run([moviepath], ['en'])
        self.assertFalse(self.handler._handle.called)
        self.assertIn("not a file", LOG.warn.call_args_list[0][0][0])

    def test_download(self):
        sub = {'lang': 'fr', 'moviepath': 'somethingthatwontexists.avi',
               'source': 'sourceTest', 'ext': '.srt'}
        self.handler._download(sub)
        self.subscope.download.assert_called_with(sub,
                                                  dest=subtitle_fname(sub))

    def test_download_sub_already_exists(self):
        moviepath = self.create_test_file('my.avi')
        self.create_test_file('my.srt')
        sub = {'lang': 'fr', 'moviepath': moviepath,
               'source': 'sourceTest', 'ext': '.srt'}
        self.handler._download(sub)
        self.assertFalse(self.subscope.download.called)

    def test_download_sub_already_exists_with_force(self):
        moviepath = self.create_test_file('my.avi')
        subpath = self.create_test_file('my.srt')
        sub = {'lang': 'fr', 'moviepath': moviepath,
               'source': 'sourceTest', 'ext': '.srt'}
        self.handler.force = True
        self.handler._download(sub)
        self.subscope.download.assert_called_with(sub, dest=subpath)


class TestDownloadFirstHandler(unittest.TestCase):
    @patch('subscope.core.LOG')
    def test_handle(self, LOG):
        subs = [
            {'lang': 'fr', 'source': 'test'},
            {'lang': 'en', 'source': 'test1'},
        ]
        handler = DownloadFirstHandler(None)
        handler._download = Mock()
        handler._handle(subs, ['fr', 'en'])
        handler._download.assert_called_with({'lang': 'fr', 'source': 'test'})


if PY2:
    MOCK_INPUT = "__builtin__.raw_input"
else:
    MOCK_INPUT = "builtins.input"


class TestDownloadInteractiveHandler(unittest.TestCase):
    def setUp(self):
        self.handler = DownloadInteractiveHandler(None)
        self.handler._download = Mock()

    def test_only_one_sub(self):
        sub = {'lang': 'fr', 'source': 'test'}
        self.handler._handle([sub], ['fr', 'en'])
        self.handler._download.assert_called_with(sub)

    @patch(MOCK_INPUT)
    def test_with_choice(self, input_):
        input_.return_value = '2'
        subs = [
            {'lang': 'fr', 'source': 'test'},
            {'lang': 'en', 'source': 'test1'},
        ]
        self.handler._handle(subs, ['fr', 'en'])
        self.handler._download.assert_called_with({'lang': 'en',
                                                   'source': 'test1'})

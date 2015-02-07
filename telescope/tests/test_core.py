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

import unittest
import tempfile
import shutil
import os

from telescope.tests import Mock

from telescope.core import Telescope, key_sub_by_langs
from telescope.sources import TelescopeSource

class TestTelescope(unittest.TestCase):
    def setUp(self):
        self.telescope = Telescope()

    def test_sources_member_is_created(self):
        self.assertIsInstance(self.telescope.sources, dict)
        # sources are all present
        self.assertEquals(sorted(self.telescope.sources.keys()),
                          sorted(TelescopeSource.REGISTRY))

    def test_search(self):
        # mock the sources
        srcs = {}
        for name, search_return in [('src1', [{}]),
                                    ('src2', [{}, {}])]:
            src = Mock()
            src.name.return_value = name
            src.search.return_value = search_return
            srcs[name] = src
        self.telescope.sources = srcs

        result = self.telescope.search('/path/to/movie', ['en'])

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

        self.telescope.sources = {'test': Mock(download=Mock(side_effect=do_download))}

        path = os.path.join(tempdir, 'my-movie.avi')
        self.telescope.download({'source': 'test', 'moviepath': path, 'ext': '.srt'})

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

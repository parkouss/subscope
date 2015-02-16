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
import os
import urllib
from StringIO import StringIO

from subscope.tests import generate_file, patch, Mock

from subscope.sources import thesubdb


class TestTheSubDBHash(unittest.TestCase):
    def test_hash(self):
        fname = generate_file(200000)
        self.addCleanup(os.unlink, fname)
        filehash = thesubdb.get_hash(fname)
        self.assertEquals(filehash, '7670cc52c96414e1f6c29cbbb6b422b5')


class TestTheSubDB(unittest.TestCase):
    def setUp(self):
        self.source = thesubdb.TheSubDB()

    @patch('subscope.sources.thesubdb.get_hash')
    @patch('requests.get')
    def test_search(self, get, get_hash):
        get_hash.return_value = '0123456'
        get.return_value = Mock(text="fr,en,ru\n")
        subs = self.source.search('/my/file.avi', ['fr', 'en'])

        get.assert_called_with(self.source.url,
                               params={'action': 'search', 'hash': '0123456'},
                               headers=self.source.headers)
        self.assertEquals(len(subs), 2)
        sub = subs[0]
        self.assertEquals(sub['lang'], 'fr')
        expected_link = '%s?%s' % (self.source.url,
                                   urllib.urlencode({'action': 'download',
                                                     'hash': '0123456',
                                                     'language': 'fr'}))
        self.assertEquals(sub['link'], expected_link)

    @patch('subscope.sources.thesubdb.get_hash')
    @patch('requests.get')
    def test_search_no_subtitles(self, get, get_hash):
        get_hash.return_value = '0123456'
        get.return_value = Mock(status_code=404)
        subs = self.source.search('/my/file.avi', ['fr', 'en'])

        self.assertEquals(len(subs), 0)

    @patch('requests.get')
    def test_download(self, get):
        subcontent = 'this is a sub'
        get.return_value = Mock(content=subcontent)
        stream = StringIO()
        self.source.download({'link': 'http://linktomysub'}, stream)

        get.assert_called_with('http://linktomysub',
                               headers=self.source.headers)
        self.assertEquals(subcontent, stream.getvalue())

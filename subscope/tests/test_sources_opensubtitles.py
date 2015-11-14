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
import requests
import gzip
import io

from subscope.tests import generate_file, patch, Mock

from subscope.sources import opensubtitles, SourceError


class TestOpenSubtitlesHash(unittest.TestCase):
    def test_hash(self):
        fname = generate_file(200000)
        self.addCleanup(os.unlink, fname)
        filehash, size = opensubtitles.hash_size_file(fname)
        self.assertEquals(filehash, '4d494e534f4e473f')
        self.assertEquals(size, 200000)

    def test_hash_file_too_small(self):
        fname = generate_file(50000)
        self.addCleanup(os.unlink, fname)
        with self.assertRaises(SourceError):
            opensubtitles.hash_size_file(fname)


class TestRequestsTransport(unittest.TestCase):
    def setUp(self):
        self.transport = opensubtitles.RequestsTransport()

    @patch('requests.post')
    def test_request(self, post):
        post.return_value = Mock(content='<some_xml/>')
        p, u = Mock(), Mock(close=Mock(return_value=1))
        self.transport.getparser = Mock(return_value=(p, u))

        res = self.transport.request('localhost', 'meth', {'p': '1'}, 1)

        headers = {'User-Agent': self.transport.user_agent,
                   "Content-Type": "text/xml"}
        post.assert_called_with('http://localhost/meth',
                                data={'p': '1'},
                                headers=headers)

        p.feed.assert_called_with('<some_xml/>')
        p.close.assert_called_with()
        u.close.assert_called_with()
        self.assertEquals(res, 1)

    @patch('requests.post')
    def test_request_transport_error(self, post):
        post.return_value = Mock(
            raise_for_status=Mock(side_effect=requests.RequestException))
        with self.assertRaises(opensubtitles.xmlrpc.ProtocolError):
            self.transport.request('localhost', 'meth', {'p': '1'}, 1)


class TestOpenSubtitles(unittest.TestCase):
    def setUp(self):
        self.source = opensubtitles.OpenSubtitles()

    @patch('subscope.sources.opensubtitles.hash_size_file')
    @patch('subscope.sources.opensubtitles.xmlrpc.Server')
    def test_search(self, Server, hash_size_file):
        server = Mock()
        Server.return_value = server
        hash_size_file.return_value = ('somehash', 123456)
        server.LogIn.return_value = {'token': 'my_token'}
        server.SearchSubtitles.return_value = {
            'data': [
                {'SubFileName': 'rel', 'SubDownloadLink': 'link',
                 'SubtitlesLink': 'page', 'SubLanguageID': 'fre'},
            ]
        }

        subs = self.source.search('/my/movie.avi', ['fr', 'en'])

        server.SearchSubtitles.assert_called_with('my_token', [{
            'moviehash': 'somehash',
            'moviebytesize': str(123456),
            'sublanguageid': 'fre,eng'
        }])

        expected = [{
            'release': 'rel',
            'link': 'link',
            'page': 'page',
            'lang': 'fr',
        }]

        self.assertEquals(subs, expected)

    @patch('requests.get')
    def test_download(self, get):
        gzipped_stream = io.BytesIO()
        with gzip.GzipFile(fileobj=gzipped_stream, mode='wb') as f:
            f.write(b'this will be gzipped!')
        get.return_value = Mock(content=gzipped_stream.getvalue())

        stream = io.BytesIO()
        self.source.download({'link': 'http://sublink'}, stream)
        self.assertEquals(stream.getvalue(), b'this will be gzipped!')

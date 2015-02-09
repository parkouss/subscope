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

from subscope.tests import generate_file

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

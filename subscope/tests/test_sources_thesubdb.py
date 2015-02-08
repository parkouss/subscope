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

from subscope.sources import thesubdb

class TestTheSubDBHash(unittest.TestCase):
    def test_hash(self):
        fname = generate_file(200000)
        self.addCleanup(os.unlink, fname)
        filehash = thesubdb.get_hash(fname)
        self.assertEquals(filehash, '7670cc52c96414e1f6c29cbbb6b422b5')

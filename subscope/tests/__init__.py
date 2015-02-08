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

try:
    from mock import Mock, patch
except ImportError:
    from unittest.mock import Mock, patch

import tempfile
import itertools

def generate_file(size, sequence='123456789'):
    f = tempfile.NamedTemporaryFile(delete=False)
    infinite = itertools.cycle(sequence)
    with f:
        for i in xrange(size):
            f.write(next(infinite).encode('ascii'))
    return f.name

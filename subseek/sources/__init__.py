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

class SourceError(Exception):
    """
    Base exception on source errors.
    """

class SubSeekSource(object):
    REGISTRY = {}

    def __init__(self):
        pass

    def name(self):
        return self.__class__.__name__

    def search(self, filename, langs):
        raise NotImplementedError

def register_source(klass):
    name = klass.__name__
    assert name not in SubSeekSource.REGISTRY
    SubSeekSource.REGISTRY[name] = klass

from .opensubtitles import OpenSubtitles

register_source(OpenSubtitles)

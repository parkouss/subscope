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

import os
import requests
import hashlib
import urllib

from subseek.sources import SubSeekSource


def get_hash(name):
    readsize = 64 * 1024
    with open(name, 'rb') as f:
        size = os.path.getsize(name)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()

class TheSubDB(SubSeekSource):
    url = 'http://api.thesubdb.com/'
    headers = {
        "User-Agent": ("SubDB/1.0 "
                       "(periscope/0.1; http://code.google.com/p/periscope)")
    }

    def search(self, filename, langs):
        filehash = get_hash(filename)
        response = requests.get(self.url,
                                params={'action': 'search', 'hash': filehash},
                                headers=self.headers)
        if response.status_code == 404:
            # no subtitle found
            return []
        subtitles = []
        for lang in response.text.splitlines()[0].split(','):
            if lang in langs:
                sublink = '%s?%s' % (self.url,
                                     urllib.urlencode({'action': 'download',
                                                       'hash': filehash ,
                                                       'language': lang}))
                subtitles.append({
                    'lang': lang,
                    'link': sublink
                })
        return subtitles

    def download(self, subtitle, stream):
        response = requests.get(subtitle["link"], headers=self.headers)
        stream.write(response.content)

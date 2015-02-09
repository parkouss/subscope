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

import os
import xmlrpclib
import struct
import logging
import requests
import gzip

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    import xmlrpc.client as xmlrpc
except ImportError:
    import xmlrpclib as xmlrpc

from subscope.sources import SubscopeSource, SourceError
from subscope import __version__

LOG = logging.getLogger(__name__)

LANG2OSLANG = {
    'af': 'afr',
    'sq': 'alb',
    'ar': 'ara',
    'hy': 'arm',
    'eu': 'baq',
    'be': 'bel',
    'bn': 'ben',
    'bs': 'bos',
    'pb': 'pob',
    'br': 'bre',
    'bg': 'bul',
    'my': 'bur',
    'ca': 'cat',
    'zh': 'chi',
    'zt': 'zht',
    'ze': 'zhe',
    'hr': 'hrv',
    'cs': 'cze',
    'da': 'dan',
    'nl': 'dut',
    'en': 'eng',
    'eo': 'epo',
    'et': 'est',
    'fi': 'fin',
    'fr': 'fre',
    'gl': 'glg',
    'ka': 'geo',
    'de': 'ger',
    'el': 'ell',
    'he': 'heb',
    'hi': 'hin',
    'hu': 'hun',
    'is': 'ice',
    'id': 'ind',
    'it': 'ita',
    'ja': 'jpn',
    'kk': 'kaz',
    'km': 'khm',
    'ko': 'kor',
    'lv': 'lav',
    'lt': 'lit',
    'lb': 'ltz',
    'mk': 'mac',
    'ms': 'may',
    'ml': 'mal',
    'ma': 'mni',
    'mn': 'mon',
    'me': 'mne',
    'no': 'nor',
    'oc': 'oci',
    'fa': 'per',
    'pl': 'pol',
    'pt': 'por',
    'ro': 'rum',
    'ru': 'rus',
    'sr': 'scc',
    'si': 'sin',
    'sk': 'slo',
    'sl': 'slv',
    'es': 'spa',
    'sw': 'swa',
    'sv': 'swe',
    'sy': 'syr',
    'tl': 'tgl',
    'ta': 'tam',
    'te': 'tel',
    'th': 'tha',
    'tr': 'tur',
    'uk': 'ukr',
    'ur': 'urd',
    'vi': 'vie',
}

OSLANG2LANG = dict((v, k) for k, v in LANG2OSLANG.iteritems())

def hash_size_file(name):
    """
    Calculates the Hash à-la Media Player Classic as it is the hash used by
    OpenSubtitles. By the way, this is not a very robust hash code.
    """
    longlongformat = 'Q' # unsigned long long little endian
    bytesize = struct.calcsize(longlongformat)
    format = "<%d%s" % (65536//bytesize, longlongformat)
    with open(name, "rb") as f:
        filesize = os.fstat(f.fileno()).st_size
        hash = filesize
        if filesize < 65536 * 2:
            raise SourceError('File is too small')
        buffer = f.read(65536)
        longlongs = struct.unpack(format, buffer)
        hash += sum(longlongs)
        f.seek(-65536, os.SEEK_END) # size is always > 131072
        buffer = f.read(65536)
        longlongs = struct.unpack(format, buffer)
        hash += sum(longlongs)
        hash &= 0xFFFFFFFFFFFFFFFF
    return "%016x" % hash, filesize

class RequestsTransport(xmlrpc.Transport):
    """
    Drop in Transport for xmlrpclib that uses Requests instead of httplib
    That allows us to use the proxies understood by requests, to define
    a timeout in a global way (TODO).

    Took from https://gist.github.com/chrisguitarguy/2354951.
    """
    # change our user agent to reflect Requests
    user_agent = "Python XMLRPC with Requests (python-requests.org)"

    def request(self, host, handler, request_body, verbose):
        """
        Make an xmlrpc request.
        """
        headers = {'User-Agent': self.user_agent}
        url = self._build_url(host, handler)
        resp = requests.post(url, data=request_body, headers=headers)
        try:
            resp.raise_for_status()
        except requests.RequestException as e:
            raise xmlrpc.ProtocolError(url, resp.status_code, 
                                       str(e), resp.headers)
        else:
            return self.parse_response(resp)

    def parse_response(self, resp):
        """
        Parse the xmlrpc response.
        """
        p, u = self.getparser()
        p.feed(resp.content)
        p.close()
        return u.close()

    def _build_url(self, host, handler):
        """
        Build a url for our request based on the host, handler and use_http
        property
        """
        return 'http://%s/%s' % (host, handler)


class OpenSubtitles(SubscopeSource):
    server_url = 'http://api.opensubtitles.org/xml-rpc'

    def search(self, filename, langs):
        filehash, filesize = hash_size_file(filename)
        search = {
            'moviehash': filehash,
            'moviebytesize': str(filesize),
            'sublanguageid': ','.join(LANG2OSLANG[l] for l in langs)
        }
        server = xmlrpc.Server(self.server_url,
                               transport=RequestsTransport())
        result = server.LogIn("", "" , "eng", "subscope %s" % __version__)
        token = result['token']
        response = server.SearchSubtitles(token, [search])
        server.LogOut(token)
        subtitles = []
        if response['data']:
            for r in response['data']:
                subtitles.append({
                    "release": r['SubFileName'],
                    "link": r['SubDownloadLink'],
                    "page": r['SubtitlesLink'],
                    "lang": OSLANG2LANG[r['SubLanguageID']]
                })
        return subtitles

    def download(self, subtitle, stream):
        response = requests.get(subtitle["link"])
        stream.write(gzip.GzipFile(fileobj=StringIO(response.content)).read())


# -*- coding: utf-8 -*-

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

from subseek.sources import SubSeekSource

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
            LOG.error('File is too small')
            return "SizeError"
        buffer = f.read(65536)
        longlongs = struct.unpack(format, buffer)
        hash += sum(longlongs)
        f.seek(-65536, os.SEEK_END) # size is always > 131072
        buffer = f.read(65536)
        longlongs = struct.unpack(format, buffer)
        hash += sum(longlongs)
        hash &= 0xFFFFFFFFFFFFFFFF
    return "%016x" % hash, filesize

class OpenSubtitles(SubSeekSource):
    server_url = 'http://api.opensubtitles.org/xml-rpc'

    def search(self, filename, langs):
        filehash, filesize = hash_size_file(filename)
        search = {
            'moviehash': filehash,
            'moviebytesize': filesize,
            'sublanguageid': ','.join(LANG2OSLANG[l] for l in langs)
        }
        server = xmlrpclib.Server(self.server_url)
        result = server.LogIn("","","eng","periscope")
        token = result['token']
        response = server.SearchSubtitles(token, [search])
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


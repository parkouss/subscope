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

from subscope.sources import SubscopeSource, SourceError
from requests.exceptions import RequestException
from threading import Thread
from Queue import Queue
from itertools import groupby
import logging
import os


LOG = logging.getLogger(__name__)

def subtitle_fname(subtitle):
    return os.path.splitext(subtitle['moviepath'])[0] + subtitle['ext']

class Subscope(object):
    def __init__(self, source_names=None):
        if source_names is None:
            source_names = SubscopeSource.REGISTRY.keys()
        self.sources = dict((name, SubscopeSource.REGISTRY[name]())
                            for name in source_names)

    def search(self, movie_path, langs):
        queue = Queue()
        for source in self.sources.itervalues():
            thread = Thread(target=self._search,
                            args=(source, queue, movie_path, langs))
            thread.start()

        subtitles = []
        for name in self.sources:
            subtitles += queue.get()
        return subtitles

    def _search(self, source, queue, movie_path, langs):
        subtitles = []
        try:
            subtitles = source.search(movie_path, langs)
        except (SourceError, RequestException) as exc:
            # do not include stacktrace here
            LOG.error("Error while searching subtitles for %s: %s",
                      source.name(), exc)
        except:
            LOG.exception('Error while searching subtitles for %s',
                          source.name())
        for sub in subtitles:
            sub['source'] = source.name()
            sub['moviepath'] = movie_path
            sub.setdefault('ext', '.srt')
        queue.put(subtitles)

    def download(self, subtitle, dest=None):
        source = self.sources[subtitle['source']]
        dest = dest or subtitle_fname(subtitle)
        with open(dest, 'wb') as stream:
            source.download(subtitle, stream)
        return dest

def key_sub_by_langs(langs):
    limit = len(langs)
    def by_lang(sub):
        try:
            return langs.index(sub['lang'])
        except ValueError:
            return limit
    return by_lang

class DownloadHandler(object):
    def __init__(self, subscope, force=False):
        self.subscope = subscope
        self.force = force

    def run(self, filepaths, langs):
        for filepath in filepaths:
            if not os.path.isfile(filepath):
                LOG.warn("Unable to get subtitles for `%s` because it is"
                         " not a file", filepath)
                continue
            subtitles = self.subscope.search(filepath, langs)
            if not subtitles:
                LOG.warn("Unable to find any subtitle for `%s`...", filepath)
            else:
                self._handle(subtitles, langs)

    def _handle(self, subtitles, langs):
        raise NotImplementedError

    def _download(self, subtitle):
        dest = subtitle_fname(subtitle)
        if not self.force and os.path.isfile(dest):
            LOG.warn("Subtitle `%s` already present, use --force to download",
                     dest)
            return
        LOG.info("Downloading subtitle [%s] from %s.",
                 subtitle['lang'],
                 subtitle['source'])
        self.subscope.download(subtitle, dest=dest)

class DownloadFirstHandler(DownloadHandler):
    def _handle(self, subtitles, langs):
        if LOG.isEnabledFor(logging.DEBUG):
            # subtitles are already grouped by source, we don't have to
            # sort them for the groupby call.
            by_source = lambda sub: sub['source']
            for source_name, subs in groupby(subtitles, by_source):
                subs = list(subs)
                nb_subs = len(subs)
                LOG.debug('%s: %d subtitle(s) found.',
                          source_name, nb_subs)
        # sort by langs
        subtitles = sorted(subtitles, key=key_sub_by_langs(langs))
        # well, just take the first one here
        self._download(subtitles[0])

class DownloadInteractiveHandler(DownloadHandler):
    def _handle(self, subtitles, langs):
        if len(subtitles) == 1:
            LOG.info("Only one subtitle found.")
            self._download(subtitles[0])
            return
        print("Choose the subtitle you want to download:")
        # format output
        line = " % 2d: [%s] %s"
        for i, sub in enumerate(subtitles):
            print(line % (i+1, sub['lang'], sub['source']))
        while 1:
            result = raw_input("> ")
            if result in [str(i+1) for i in range(len(subtitles))]:
                result = int(result) - 1
                break
        self._download(subtitles[result])

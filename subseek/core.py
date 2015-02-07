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

from subseek.sources import SubSeekSource, SourceError
from threading import Thread
from Queue import Queue
from itertools import groupby
import logging
import os


LOG = logging.getLogger(__name__)

class SubSeek(object):
    def __init__(self, source_names=None):
        if source_names is None:
            source_names = SubSeekSource.REGISTRY.keys()
        self.sources = dict((name, SubSeekSource.REGISTRY[name]())
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
        except SourceError as exc:
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

    def download(self, subtitle):
        source = self.sources[subtitle['source']]
        dest = os.path.splitext(subtitle['moviepath'])[0] + subtitle['ext']
        with open(dest, 'wb') as stream:
            source.download(subtitle, stream)
        return dest

def sub_by_source(subtitle):
    return subtitle['source']

class DownloadFirstHandler(object):
    def __init__(self, subseek):
        self.subseek = subseek

    def run(self, filepaths, langs):
        for filepath in filepaths:
            subtitles = self.subseek.search(filepath, langs)
            if not subtitles:
                LOG.warn("Unable to find any subtitle for %s...", filepath)
            else:
                if LOG.isEnabledFor(logging.DEBUG):
                    # subtitles are already grouped by source, we don't have to
                    # sort them for the groupby call.
                    for source_name, subs in groupby(subtitles, sub_by_source):
                        subs = list(subs)
                        nb_subs = len(subs)
                        LOG.debug('%s: %d subtitle(s) found.',
                                  source_name, nb_subs)
                # well, just take the first one here
                self._download(subtitles[0])

    def _download(self, subtitle):
        LOG.info("Downloading subtitle from %s.", subtitle['source'])
        self.subseek.download(subtitle)

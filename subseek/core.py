from subseek.sources import SubSeekSource
import subseek.sources.opensubtitles
from threading import Thread
from Queue import Queue
import logging
import os

LOG = logging.getLogger()

class SubSeek(object):
    def __init__(self):
        self.sources = dict((name, klass())
                            for name, klass in SubSeekSource.REGISTRY.iteritems())

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
        try:
            subtitles = source.search(movie_path, langs)
        except:
            LOG.exception('Error while searching subtitles for %s',
                          source.name())
            subtitles = []
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

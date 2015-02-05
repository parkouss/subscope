
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

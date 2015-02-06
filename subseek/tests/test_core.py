import unittest
try:
    from mock import Mock
except ImportError:
    from unittest.mock import Mock

from subseek.core import SubSeek
from subseek.sources import SubSeekSource

class TestSubSeek(unittest.TestCase):
    def setUp(self):
        self.subseek = SubSeek()

    def test_sources_member_is_created(self):
        self.assertIsInstance(self.subseek.sources, dict)
        # sources are all present
        self.assertEquals(sorted(self.subseek.sources.keys()),
                          sorted(SubSeekSource.REGISTRY))

    def test_search(self):
        # mock the sources
        srcs = {}
        for name, search_return in [('src1', [{}]),
                                    ('src2', [{}, {}])]:
            src = Mock()
            src.name.return_value = name
            src.search.return_value = search_return
            srcs[name] = src
        self.subseek.sources = srcs

        result = self.subseek.search('/path/to/movie', ['en'])

        srcs['src1'].search.assert_called_with('/path/to/movie', ['en'])
        srcs['src2'].search.assert_called_with('/path/to/movie', ['en'])

        expected = [
            {'moviepath': '/path/to/movie', 'source': 'src2', 'ext': '.srt'},
            {'moviepath': '/path/to/movie', 'source': 'src2', 'ext': '.srt'},
            {'moviepath': '/path/to/movie', 'source': 'src1', 'ext': '.srt'}]
        self.assertEquals(sorted(r.items() for r in result),
                          sorted(r.items() for r in expected))

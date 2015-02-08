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
import re
import sys

from setuptools import setup

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

def read(*parts):
    return open(os.path.join(THIS_DIR, *parts)).read()

def version():
    return re.findall("__version__ = '([\d\.]+)'",
                      read('subscope', '__init__.py'))[0]

tests_require = []
if sys.version_info < (3, 3):
    tests_require.append('mock')

setup(name='subscope',
      version=version(),
      author=u"Julien Pagès",
      author_email="j.parkouss@gmail.com",
      description=("A command line tool to download subtitles for your "
                   "movies."),
      long_description=read("README.rst"),
      keywords="subtitles movies srt download opensubtitles thesubdb",
      license="GPLv3",
      packages=['subscope', 'subscope.sources', 'subscope.tests'],
      classifiers=["Development Status :: 3 - Alpha",
                   "Topic :: Utilities",
                   "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                   "Environment :: Console",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.4"],
      install_requires=["requests"],
      entry_points={
        'console_scripts': ['subscope = subscope.main:main']
      },
      test_suite="subscope.tests",
      tests_require=tests_require,
      use_2to3=True,
)

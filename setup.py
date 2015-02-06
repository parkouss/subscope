# -*- coding: utf-8 -*-
import os
import re
import sys

from setuptools import setup

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

def read(*parts):
    return open(os.path.join(THIS_DIR, *parts)).read()

def version():
    return re.findall("__version__ = '([\d\.]+)'",
                      read('subseek', '__init__.py'))[0]

tests_require = []
if sys.version_info < (3, 3):
    tests_require.append('mock')

setup(name='subseek',
      version=version(),
      author=u"Julien Pagès",
      author_email="j.parkouss@gmail.com",
      description=("A command line tool to download subtitles for your "
                   "movies."),
      long_description=read("README.rst"),
      keywords="subtitles movies srt opensubtitles",
      license="GPLv3",
      packages=['subseek', 'subseek.sources', 'subseek.tests'],
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
        'console_scripts': ['subseek = subseek.main:main']
      },
      test_suite="subseek.tests",
      tests_require=tests_require,
      use_2to3=True,
)

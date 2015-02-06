# -*- coding: utf-8 -*-
import os
import re

from setuptools import setup

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

def read(*parts):
    return open(os.path.join(THIS_DIR, *parts)).read()

def version():
    return re.findall("__version__ = '([\d\.]+)'",
                      read('subseek', '__init__.py'))[0]

setup(name='subseek',
      version=version(),
      author=u"Julien Pagès",
      author_email="j.parkouss@gmail.com",
      description=("A command line tool to download subtitles for your "
                   "movies."),
      long_description=read("README.rst"),
      keywords="subtitles movies srt opensubtitles",
      license="GPLv3",
      packages=['subseek', 'subseek.sources'],
      classifiers=["Development Status :: 3 - Alpha",
                   "Topic :: Utilities",
                   "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                   "Environment :: Console",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 2.7"],
      install_requires=["requests"],
      entry_points={
        'console_scripts': ['subseek = subseek.main:main']
      },
      test_suite="subseek.tests",
      tests_require=['mock'],
)

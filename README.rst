subscope
========

A command line tool to download subtitles for your movies.

See the `project page`_ for more documentation.

.. image:: https://travis-ci.org/parkouss/subscope.svg?branch=master
    :target: https://travis-ci.org/parkouss/subscope
.. image:: https://coveralls.io/repos/parkouss/subscope/badge.svg?branch=master
    :target: https://coveralls.io/r/parkouss/subscope?branch=master

Installation
------------

To install or update subscope, simply: ::

  pip install -U subscope

Basic use
---------

This is how you can download subtitles for your movies: ::

  subscope -l fr,en /path/to/my/movie1.avi /path/to/my/movie2.mkv

How to contribute
-----------------

Just send pull requests here. Here is a way to create a working dev
environment: ::

  # checkout the code
  git clone https://github.com/parkouss/subscope
  cd subscope

  # create a virtualenv and install subscope in it
  virtualenv venv
  . venv/bin/activate
  pip install -e .

  # run tests
  pip install mock # not required, and only for python < 3.3 users
  python setup.py test


Thanks to
---------

The original idea comes from the `periscope`_ project, so many thanks to
its author and contributors! Unfortunatly the project is not active since
Dec 2013, that's the reason why subscope exists now.

.. _periscope: https://github.com/patrickdessalle/periscope

.. _project page: http://parkouss.github.io/subscope

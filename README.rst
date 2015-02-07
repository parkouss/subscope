telescope
=======

A command line tool to download subtitles for your movies.


Installation
------------

To install or update telescope, simply: ::

  pip install -U telescope

Basic use
---------

This is how you can download subtitles for your movies: ::

  telescope -l fr,en /path/to/my/movie1.avi /path/to/my/movie2.mkv

How to contribute
-----------------

Just send pull requests here. Here is a way to create a working dev
environment: ::

  # checkout the code
  git clone https://github.com/parkouss/telescope
  cd telescope

  # create a virtualenv and install telescope in it
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
Dec 2013, that's the reason why telescope exists now.

.. _periscope: https://github.com/patrickdessalle/periscope

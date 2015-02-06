subseek
=======

A command line tool to download subtitles for your movies.


Installation
------------

To install or update subseek, simply: ::

  pip install -U subseek

Basic use
---------

This is how you can download subtitles for your movies: ::

  subseek -l fr,en /path/to/my/movie1.avi /path/to/my/movie2.mkv

How to contribute
-----------------

Just send pull requests here. Here is a way to create a working dev
environment: ::

  # checkout the code
  git clone https://github.com/parkouss/subseek
  cd subseek

  # create a virtualenv and install subseek in it
  virtualenv venv
  . venv/bin/activate
  pip install -e .

  # run tests
  pip install mock # not required, and only for python < 3.3 users
  python setup.py test

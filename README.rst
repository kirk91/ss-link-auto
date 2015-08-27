ss-link-auto
===========

Auto acquire ss-link free shadowsocks accounts

Versions
--------

auto-ss works with Python2.7+


Installation
------------

pip / easy\_install
~~~~~~~~~~~~~~~~~~~

.. code:: bash
    $ pip install auto-ss

or

.. code:: bash
    $ easy_install auto-ss

Github
~~~~~~

.. code:: bash
    $ pip install git+https://github.com/steven-hl/ss-link-auto.git

Usage
-----

.. code:: bash
    $ auto-ss -h

    usage: auto-ss [-h] [--mode MODE] [--timeout TIMEOUT] email password

    Auto acquire ss-link free shadowsocks accounts.

    positional arguments:
      email              ss-link email
      password           ss-link password

    optional arguments:
      -h, --help         show this help message and exit
      --mode MODE        run mode, deault `avaiable`. if mode is `speed`, will
                         test network connection
      --timeout TIMEOUT  connection timeout in seconds, default 10

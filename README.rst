ss-link-auto
============

Auto acquire `ss-link <https://www.ss-link.com/>`_  free shadowsocks accounts


If you want to use auto-ss, you need to registr a `ss-link account <https://www.ss-link.com/register>`_ . Free shadowsocks accounts will be invalid in **a period time**, If accounts are invalid, you need to run ``auto-ss`` again


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


Note
----

If you run auto-ss in mode ``speed`` or ``run``, you need install `shadowsocks <https://github.com/shadowsocks/shadowsocks>`_
firstly.

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

Demo
----

Run in avaiable mode
~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    ➜  ~  auto-ss xxx@xxx.com xxx
    ############### 2015-08-27 23:19:30 Shadowsocks Accounts ###############
    server_address       server_port    server_password      encrypt_method
    ========================================================================
    76.164.197.155           9980           82057967          aes-256-cfb
    72.46.135.119            9980           82057967          aes-256-cfb
    173.252.220.201          9980           82057967          aes-256-cfb
    104.250.144.10           9980           82057967          aes-256-cfb
    104.250.143.243          9980           82057967          aes-256-cfb
    104.250.146.37           9980           82057967          aes-256-cfb
    104.250.146.212          9980           82057967          aes-256-cfb
    104.250.147.22           9980           82057967          aes-256-cfb

Run in speed mode
~~~~~~~~~~~~~~~~~

It will test shadowsocks conection speed by view https://www.google.com.hk

.. code:: bash

    ➜  ~  auto-ss xxx@xxx.com xxxx --mode speed
    ############### 2015-08-27 23:29:56 Shadowsocks Accounts ###############
    server_address       server_port    server_password      encrypt_method
    ========================================================================
    76.164.197.155           9980           82057967          aes-256-cfb
    72.46.135.119            9980           82057967          aes-256-cfb
    173.252.220.201          9980           82057967          aes-256-cfb
    104.250.146.212          9980           82057967          aes-256-cfb
    104.250.144.10           9980           82057967          aes-256-cfb
    104.250.143.243          9980           82057967          aes-256-cfb
    104.250.146.37           9980           82057967          aes-256-cfb
    104.250.147.22           9980           82057967          aes-256-cfb

    ########################### Connection Test ############################
    76.164.197.155                                            speed is: 6kb/s
    72.46.135.119                                             speed is: 8kb/s
    173.252.220.201                                           speed is: 3kb/s
    104.250.146.212                                           speed is: 9kb/s
    104.250.144.10                                            speed is: 7kb/s
    104.250.143.243                                           speed is: 7kb/s
    104.250.146.37                                            speed is: 4kb/s
    104.250.147.22                                            speed is: 8kb/s


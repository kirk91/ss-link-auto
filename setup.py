#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

__version__ = '0.1.3'

setup(
    name='auto-ss',
    version=__version__,
    description=('Auto acquire ss-link free shadowsocks accounts'
                 ' and test connection speed'),
    author='Steven Han',
    author_email='steven.hl.0901@gmail.com',
    url='https://github.com/steven-hl/ss-link-auto',
    license='ISC',
    long_description=open('README.rst').read(),
    py_modules=['auto_ss'],
    package_data={"": ["LICENSE"]},
    entry_points={
        'console_scripts': [
            'auto-ss=auto_ss:main',
        ]
    },
    install_requires=[
        'requests==2.7.0',
        'requesocks==0.10.8',
        'beautifulsoup4==4.3.2',
    ],
)

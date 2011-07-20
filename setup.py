#!/usr/bin/env python
# -*- coding: utf-8 -
#
# This file is part of http-parser released under the MIT license.
# See the NOTICE for more information.

from distribute_setup import use_setuptools
use_setuptools()

from imp import load_source
from setuptools import setup, find_packages, Extension, Feature
import os
import sys

if not hasattr(sys, 'version_info') or \
        sys.version_info < (2, 5, 0, 'final'):
    raise SystemExit("http-parser requires Python 2.6x or later")

IS_PYPY = hasattr(sys, 'pypy_version_info')
VERSION = load_source('http_parser', os.path.join('http_parser',
    '__init__.py')).__version__
DESCRIPTION = 'http request/response parser'
LONG_DESCRIPTION = open('README.rst', 'r').read()
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Other Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Topic :: Internet',
    'Topic :: Utilities',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

speedups = Feature(
    'optional C speed-enhancement module',
    standard=True,
    ext_modules = [
        Extension('http_parser.parser', [
            'http_parser/parser.pyx', 'http_parser/http_parser.c'
        ], ['http_parser']),
    ],
)

def main(with_binary):
    if with_binary:
        features = {'speedups': speedups}
    else:
        features = {}

    extra = {}

    # Python 3: run 2to3
    if sys.version_info >= (3,):
        extra['use_2to3'] = True

    setup(
        name='http-parser',
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author='Benoit Chesneau',
        author_email='benoitc@e-engura.com',
        license='MIT',
        url='http://github.com/benoitc/http-parser',
        classifiers=CLASSIFIERS,
        packages=find_packages(),
        # data_files=[('http_parser',
        #     ['LICENSE', 'MANIFEST.in', 'NOTICE', 'README.rst', 'THANKS']
        # )],
        features=features,
        **extra
    )


if __name__ == "__main__":
    main(not IS_PYPY)

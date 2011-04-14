# -*- coding: utf-8 -
#
# This file is part of http-parser released under the MIT license. 
# See the NOTICE for more information.

from __future__ import with_statement

from distutils.core import setup
from distutils.extension import Extension
import glob
from imp import load_source
import os
import sys



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


MODULES = ["http_parser"]

def main():
    try:
        import Cython
        from Cython.Distutils import build_ext
    except ImportError:
        Cython = None
        print >> sys.stderr, 'No cython found, cannot rebuild parser.c'
        sys.exit(1)


    
    http_parser = load_source("http_parser", os.path.join("http_parser",
        "__init__.py"))

    # read long description
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
        long_description = f.read()

    PACKAGES = {}
    for name in MODULES:
        PACKAGES[name] = name.replace(".", "/")

    print PACKAGES
    DATA_FILES = [
        ('http_parser', ["LICENSE", "MANIFEST.in", "NOTICE", "README.rst",
                        "THANKS",])
        ]
    

    options = dict(
            name = 'http-parser',
            version = http_parser.__version__,
            description = 'http request/response parser',
            long_description = long_description,
            author = 'Benoit Chesneau',
            author_email = 'benoitc@e-engura.com',
            license = 'MIT',
            url = 'http://github.com/benoitc/http-parser',
            classifiers = CLASSIFIERS,
            packages = PACKAGES.keys(),
            package_dir = PACKAGES,
            data_files = DATA_FILES
    )

    if Cython is not None:
        INCLUDE_DIRS = ["http_parser"]
        SOURCES = [os.path.join("http_parser", "parser.pyx"),
                os.path.join("http_parser", "http_parser.c")]

        EXT_MODULES = [Extension("http_parser.parser", 
            sources=SOURCES, include_dirs=INCLUDE_DIRS)]

        extra = dict(
                cmdclass = {'build_ext': build_ext},
                ext_modules = EXT_MODULES
        )

        options.update(extra)

    setup(**options)

if __name__ == "__main__":
    main()

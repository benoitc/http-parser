# -*- coding: utf-8 -
#
# This file is part of http-parser released under the MIT license.
# See the NOTICE for more information.

from __future__ import with_statement
from distutils.errors import CCompilerError, DistutilsExecError, \
    DistutilsPlatformError
from distutils.command.build_ext import build_ext
from distutils.command.sdist import sdist as _sdist
import glob
from imp import load_source
import io
import os
import shutil
import sys
import traceback

from setuptools import setup, find_packages, Extension, Feature

if not hasattr(sys, 'version_info') or \
        sys.version_info < (2, 6, 0, 'final'):
    raise SystemExit("http-parser requires Python 2.6x or later")

ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError)
if sys.platform == 'win32' and sys.version_info > (2, 6):
   # 2.6's distutils.msvc9compiler can raise an IOError when failing to
   # find the compiler
   ext_errors += (IOError,)

http_parser = load_source("http_parser", os.path.join("http_parser",
        "__init__.py"))

IS_PYPY = hasattr(sys, 'pypy_version_info')
CLASSIFIERS = [
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
VERSION = http_parser.__version__

# get long description
with io.open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf8') as f:
    LONG_DESCRIPTION = f.read()

def _system(cmd):
    cmd = ' '.join(cmd)
    sys.stderr.write('Running %r in %s\n' % (cmd, os.getcwd()))
    return os.system(cmd)

def make(done=[]):
    if not done:
        if os.path.exists('Makefile'):
            if "PYTHON" not in os.environ:
                os.environ["PYTHON"] = sys.executable
            if os.system('make'):
                sys.exit(1)
        done.append(1)

class sdist(_sdist):

    def run(self):
        renamed = False
        if os.path.exists('Makefile'):
            make()
            os.rename('Makefile', 'Makefile.ext')
            renamed = True
        try:
            return _sdist.run(self)
        finally:
            if renamed:
                os.rename('Makefile.ext', 'Makefile')

class BuildFailed(Exception):
    pass

class my_build_ext(build_ext):

    def build_extension(self, ext):
        make()
        try:
            result = build_ext.build_extension(self, ext)
        except ext_errors:
            if getattr(ext, 'optional', False):
                raise BuildFailed
            else:
                raise
        # hack: create a symlink from build/../core.so to
        # http_parser/parser.so
        # to prevent "ImportError: cannot import name core" failures
        try:
            fullname = self.get_ext_fullname(ext.name)
            modpath = fullname.split('.')
            filename = self.get_ext_filename(ext.name)
            filename = os.path.split(filename)[-1]
            if not self.inplace:
                filename = os.path.join(*modpath[:-1] + [filename])
                path_to_build_core_so = os.path.abspath(os.path.join(self.build_lib,
                    filename))
                path_to_core_so = os.path.abspath(os.path.join('http_parser',
                    os.path.basename(path_to_build_core_so)))
                if path_to_build_core_so != path_to_core_so:
                    try:
                        os.unlink(path_to_core_so)
                    except OSError:
                        pass
                    if hasattr(os, 'symlink'):
                        sys.stderr.write('Linking %s to %s\n' % (
                            path_to_build_core_so, path_to_core_so))
                        os.symlink(path_to_build_core_so, path_to_core_so)
                    else:
                        sys.stderr.write('Copying %s to %s\n' % (
                            path_to_build_core_so, path_to_core_so))
                        shutil.copyfile(path_to_build_core_so, path_to_core_so)
        except Exception:
            traceback.print_exc()
        return result


def run_setup(with_binary):
    extra = {}
    if with_binary:
        extra.update(dict(
            ext_modules = [
                Extension('http_parser.parser', [
                    os.path.join('http_parser', 'http_parser.c'),
                    os.path.join('http_parser', 'parser.c')
                ], ['parser'])],
            cmdclass=dict(build_ext=my_build_ext, sdist=sdist)
        ))


    setup(
        name = 'http-parser',
        version = VERSION,
        description = 'http request/response parser',
        long_description = LONG_DESCRIPTION,
        author = 'Benoit Chesneau',
        author_email = 'benoitc@e-engura.com',
        license = 'MIT',
        url = 'http://github.com/benoitc/http-parser',
        classifiers = CLASSIFIERS,
        platforms=['any'],
        packages = find_packages(),
        ** extra
    )


if __name__ == "__main__":
    run_setup(not IS_PYPY)

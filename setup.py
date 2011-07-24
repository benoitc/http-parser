# -*- coding: utf-8 -
#
# This file is part of http-parser released under the MIT license. 
# See the NOTICE for more information.

from __future__ import with_statement

from distutils.core import setup
from distutils.command import build_ext
from distutils.command.install import INSTALL_SCHEMES
from distutils.extension import Extension
from distutils.errors import CCompilerError, DistutilsExecError
import glob
from imp import load_source
import os
import sys
import traceback

if not hasattr(sys, 'version_info') or \
        sys.version_info < (2, 5, 0, 'final'):
    raise SystemExit("http-parser requires Python 2.6x or later")

is_pypy = hasattr(sys, 'pypy_version_info')

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

INCLUDE_DIRS = ["http_parser"]
SOURCES = [os.path.join("http_parser", "parser.c"),
        os.path.join("http_parser", "http_parser.c")]

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

class my_build_ext(build_ext.build_ext):
    user_options = (build_ext.build_ext.user_options
                    + [("cython=", None, "path to the cython executable")])

    def initialize_options(self):
        build_ext.build_ext.initialize_options(self)
        self.cython = "cython"

    def compile_cython(self):
        sources = glob.glob('http_parser/*.pyx')
        if not sources:
            if not os.path.exists('http_parser/parser.c'):
                sys.stderr.write('Could not find http_parser/parser.c\n')

        if os.path.exists('http_parser/parser.c'):
            core_c_mtime = os.stat('http_parser/parser.c').st_mtime
            changed = [filename for filename in sources if \
                    (os.stat(filename).st_mtime - core_c_mtime) > 1]
            if not changed:
                return
            sys.stderr.write('Running %s (changed: %s)\n' % (self.cython, 
                ', '.join(changed)))
        else:
            sys.stderr.write('Running %s' % self.cython)
        cython_result = os.system('%s http_parser/parser.pyx' % self.cython)
        if cython_result:
            if os.system('%s -V 2> %s' % (self.cython, os.devnull)):
                # there's no cython in the system
                sys.stderr.write('No cython found, cannot rebuild parser.c\n')
                return
            sys.exit(1)

    def build_extension(self, ext):
        if self.cython:
            self.compile_cython()
        try:
            result = build_ext.build_ext.build_extension(self, ext)
            # hack: create a symlink from build/../parser.so to http_parser/parser.so
            # to prevent "ImportError: cannot import name core" failures

            fullname = self.get_ext_fullname(ext.name)
            modpath = fullname.split('.')
            filename = self.get_ext_filename(ext.name)
            filename = os.path.split(filename)[-1]
            if not self.inplace:
                filename = os.path.join(*modpath[:-1] + [filename])
                path_to_build_core_so = os.path.abspath(
                        os.path.join(self.build_lib, filename))
                path_to_core_so = os.path.abspath(
                        os.path.join('http_parser', 
                            os.path.basename(path_to_build_core_so)))
                if path_to_build_core_so != path_to_core_so:
                    try:
                        os.unlink(path_to_core_so)
                    except OSError:
                        pass
                    if hasattr(os, 'symlink'):
                        print('Linking %s to %s' % (path_to_build_core_so, 
                            path_to_core_so))
                        os.symlink(path_to_build_core_so, path_to_core_so)
                    else:
                        print('Copying %s to %s' % (path_to_build_core_so, 
                            path_to_core_so))
                        import shutil
                        shutil.copyfile(path_to_build_core_so, path_to_core_so)
            return result

        except (Exception, CCompilerError,):
            traceback.print_exc()
            sys.stderr.write("warning: can't build parser.c speedup.\n\n")
            sys.stderr.write("You can can safely ignire previous error.\n")

        

def main():
    http_parser = load_source("http_parser", os.path.join("http_parser",
        "__init__.py"))

    # read long description
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
        long_description = f.read()

    PACKAGES = {}
    for name in MODULES:
        PACKAGES[name] = name.replace(".", "/")

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
            platforms=['any'],
            packages = PACKAGES.keys(),
            package_dir = PACKAGES,
            data_files = DATA_FILES,
            
    )


    if not is_pypy:
        EXT_MODULES = [Extension("http_parser.parser", 
            sources=SOURCES, include_dirs=INCLUDE_DIRS)]


        options.update(dict(
            cmdclass = {'build_ext': my_build_ext},
            ext_modules = EXT_MODULES))

    # Python 3: run 2to3
    try:
        from distutils.command.build_py import build_py_2to3
        from distutils.command.build_scripts import build_scripts_2to3
    except ImportError:
        pass
    else:
        options['cmdclass'].update({
            'build_py': build_py_2to3,
            'build_scripts': build_scripts_2to3,
        })
    

    setup(**options)

if __name__ == "__main__":
    main()


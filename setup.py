# setup.py for planar
#
# $Id$

import os
import sys
import shutil
from distutils.core import setup, Extension

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    if sys.version_info >= (3, 0):
        raise ImportError("build_py_2to3 not found in distutils - it is required for Python 3.x")
    from distutils.command.build_py import build_py
    suffix = ""
else:
    suffix = "-py3k"

srcdir = os.path.dirname(__file__)

def read(fname):
    return open(os.path.join(srcdir, fname)).read()

include_dirs = ['include']
extra_compile_args = []

if 'SETUP_PY_CFLAGS' in os.environ:
	# SETUP_PY_CFLAGS allows you to pass in CFLAGS
	# in a disutils-friendly way. Using CFLAGS directly
	# causes linking to fail for some python versions
	extra_compile_args.append(os.environ['SETUP_PY_CFLAGS'])

setup(
    name='planar',
    version='0.3', # *** REMEMBER TO UPDATE __init__.py ***
    description='2D planar geometry library for Python.',
    long_description=read('README.txt'),
    provides=['planar'],
    author='Casey Duncan',
    author_email='casey.duncan@gmail.com',
    url='http://bitbucket.org/caseman/planar/',
    license='BSD',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
    ],
    platforms = 'any',

    package_dir={'planar': 'lib/planar',
                 'planar.test': 'test'},
    packages=['planar', 'planar.test'], 
	ext_modules=[
		Extension('planar.c', 
			['lib/planar/cmodule.c', 
			 'lib/planar/cvector.c',
			 'lib/planar/ctransform.c',
			 'lib/planar/cbox.c',
			 'lib/planar/cpolygon.c',
			], 
			include_dirs=include_dirs,
			#library_dirs=library_dirs,
			#libraries=libraries,
			#extra_link_args=extra_link_args,
			extra_compile_args=extra_compile_args,
			#define_macros=macros,
		),
    ],

    cmdclass = {'build_py': build_py},
)

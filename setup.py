#! /usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os
from setuptools import setup
from setuptools.command.test import test as TestCommand
import versioneer

HERE = os.path.abspath(os.path.dirname(__file__))

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['test']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


__cmdclass_arg__ = versioneer.get_cmdclass()
__cmdclass_arg__.update({'test': PyTest})



__project__      = 'wine-vision'
__author__       = 'merry31'
__author_email__ = 'julien.rallo@gmail.com'
__url__          = 'https://github.com/PolarTeam/wine-vision'
__platforms__    = 'ALL'

__classifiers__ = [
    'Development Status :: 1 - Alpha',
    'Programming Language :: Python :: 2.7'

    'Environment :: Console',
    'Intended Audience :: Developers',
    'Operating System :: POSIX :: Linux',
    'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
    ]

__keywords__ = [
    'raspberrypi',
    'camera',
    'wine',
    ]

__requires__ = [
    'pygame'
    ]

__extra_requires__ = {
    'doc':   ['sphinx'],
    'test':  ['coverage', 'pytest'],
    }

__entry_points__ = {
    }

__scripts__ = [
    'cam.py'
    ]


if __name__ == '__main__':
    import io
    with io.open(os.path.join(HERE, 'README.md'), 'r') as readme:
        setup(
            name                 = __project__,
            description          = __doc__,
            long_description     = readme.read(),
            classifiers          = __classifiers__,
            author               = __author__,
            author_email         = __author_email__,
            url                  = __url__,
            keywords             = __keywords__,
            packages             = find_packages(),
            scripts              = __scripts__,
            include_package_data = True,
            platforms            = __platforms__,
            install_requires     = __requires__,
            extras_require       = __extra_requires__,
            entry_points         = __entry_points__,
            cmdclass             = __cmdclass_arg__,
            )

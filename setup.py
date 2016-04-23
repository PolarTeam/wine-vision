#! /usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os
from setuptools import setup
from setuptools.command.test import test as TestCommand
import versioneer

LONG=''
with open('README.md') as readme:
  LONG=readme.read()

requirements = []
with open('requirements.txt') as req:
    requirements=req.readline()


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


cmdclass_arg = versioneer.get_cmdclass()
cmdclass_arg.update({'test': PyTest})

setup(name='wine-vision',
      description='Wine vision description.',
      long_description=LONG,
      author='merry31',
      author_email='julien.rallo@gmail.com',
      install_requires=requirements,
      license='Apache',
      url='https://github.com/PolarTeam/wine-vision',
      version=versioneer.get_version(),
      scripts = [
        'cam.py'
        ],
      packages=[
        'winevision',
        ],
      tests_require=['pytest'],
      cmdclass=cmdclass_arg,
      classifiers=['Development Status :: 1 - Alpha',
                   'Programming Language :: Python :: 2.7'])

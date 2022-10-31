#!/usr/bin/env python

import os
import sys

from setuptools import find_packages
from setuptools.command.test import test as TestCommand

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation can be generated with Sphinx"""

history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requires = []
tests_require = ['pytest>=2.3']

PACKAGE_PATH = os.path.abspath(os.path.join(__file__, os.pardir))

setup(
    name='ivory',
    version='0.0.1',
    description='Simple and flexible workflow engine',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='',
    author_email='',
    url='',
    packages=find_packages(PACKAGE_PATH),
    package_dir={'ivory': 'ivory'},
    include_package_data=True,
    install_requires=requires,
    license='GPLv3',
    zip_safe=False,
    keywords='ivory',
    entry_points={
        'console_scripts': [
            'ivory = ivory.cli.main:run',
        ]
    },

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        "Intended Audience :: Science/Research",
        'Intended Audience :: Developers',
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        'Natural Language :: English',
        'Programming Language :: Python :: 3.10',
    ],
    tests_require=tests_require,
    cmdclass={'test': PyTest},
)

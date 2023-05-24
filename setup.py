import os

from setuptools import setup, find_packages

PACKAGE_PATH = os.path.abspath(os.path.join(__file__, os.pardir))

setup(
    name='ivory',
    version='0.0.1',
    description='Ivory: Simple and flexible workflow engine ',
    author='',
    author_email='',
    packages=find_packages(PACKAGE_PATH),
    install_requires=[
        'numpy~=1.23.3',
        'py~=1.11.0',
        'pytest~=7.1.3',
        'setuptools~=59.6.0',
        'joblib',
        'ipyparallel',
    ],
    classifiers=[
        'GPLv3',
        'Programming Language :: Python :: 3.10',
    ],
)

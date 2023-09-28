#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()

def package_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

example_files = package_files('examples')

from setuptools import find_packages
setup(
    name='pytest_donde',
    version='0.0.31',
    author='Clemens Löbner',
    author_email='mikamove@posteo.de',
    maintainer='Clemens Löbner',
    maintainer_email='mikamove@posteo.de',
    license='MIT',
    url='https://github.com/mikamove/pytest-donde',
    description='record pytest session characteristics per test item (coverage and duration) into a persistent file and use them in your own plugin or script.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    py_modules=['pytest_donde'],
    python_requires='>=3.8',
    install_requires=[
        'pytest>=7.3.1',
        'pytest-cov>=4.1.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'donde = pytest_donde.plugin',
        ],
    },
    packages=find_packages(where='.'),
    package_dir={'': '.'},
    package_data={'': example_files},
 )

# -*- coding: utf-8 -*-
#!/bin/env python3

# Copyright (C) 2003-2007 Gaby Launay

# Author: Gaby Launay  <gaby.launay@tutanota.com>
# URL: https://framagit.org/gabylaunay/pyDSA_gui

# This file is part of pyDSA_gui

# pyDSA_gui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), "r") as fh:
    long_description = fh.read()

setup(
    name='pyDSA_gui',
    version='1.2.5',
    description='GUI for pyDSA_core',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://framagit.org/gabylaunay/pyDSA_gui',
    author='Gaby Launay',
    author_email='gaby.launay@protonmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 3.5',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
    ],
    keywords='GUI DSA drop shape contact angle hysteresis',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'samples']),
    install_requires=['pyQt5', 'pyDSA_core==1.2.2', 'IMTreatment==1.2.0',
                      'numpy', 'matplotlib>=2.2.0'],
    extras_require={},
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pyDSA = pyDSA_gui.MainApp:run',
        ],
    },
    zip_safe=False,
)

# -*- coding: utf-8 -*-
#!/bin/env python3

# Copyright (C) 2003-2007 Gaby Launay

# Author: Gaby Launay  <gaby.launay@tutanota.com>
# URL: https://framagit.org/gabylaunay/pyDSA-qt5
# Version: 0.1

# This file is part of pyDSA-qt5

# pyDSA-qt5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from setuptools import setup, find_packages

setup(
    name='pyDSAqt5',
    version='1.0',
    description='GUI for pydsa',
    author='Gaby Launay',
    author_email='gaby.launay@tutanota.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 3.5',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
    ],
    keywords='GUI DSA drop shape contact angle hysteresis',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'samples']),
    install_requires=['pyQt5', 'pyDSA==1.0', 'IMTreatment==1.0', 'numpy',
                      'matplotlib'],
    extras_require={},
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pyDSAqt5 = pyDSAqt5.MainApp:run',
        ],
    },
    zip_safe=False,
)

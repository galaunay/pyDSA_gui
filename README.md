# pyDSAqt5

PyDSAqt5 is a graphical interface for [pyDSA](https://framagit.org/gabylaunay/pyDSA), a drop shape analyzer.

## Dependencies

pyDSAqt5 relies on pyDSA and pyQt5

## Installation

### Linux

You will need [git](https://git-scm.com/) to be installed.

To install the dependencies that are not available on pipy, run:

``pip install 'git+https://framagit.org/gabylaunay/IMTreatment.git#egg=IMTreatment'``.

``pip install 'git+https://framagit.org/gabylaunay/pyDSA.git#egg=pyDSA'``.

Then install pyDSAqt5:

``pip install 'git+https://framagit.org/gabylaunay/pyDSAqt5.git#egg=pyDSAqt5'``

### Anaconda

Install git with:

``conda install git``

Install the dependencies:

``pip install git+https://framagit.org/gabylaunay/IMTreatment.git#egg=IMTreatment``.

``pip install git+https://framagit.org/gabylaunay/pyDSA.git#egg=pyDSA``.

And finally install pyDSAqt5:

``pip install git+https://framagit.org/gabylaunay/pyDSAqt5.git#egg=pyDSAqt5``

## Usage

Just fire the GUI from the terminal (or anaconda console) with:

``pyDSAqt5``

## Issues and bugs

If pyDSAqt5 crashes or behave abnormally, you can report [here](https://framagit.org/gabylaunay/pyDSAqt5/issues) or just send me an email at [gaby.launay@northumbria.ac.uk](mailto:gaby.launay@northumbria.ac.uk), with

- a description of the problem (as detailled as possible, for me to get it)
- the logs from the terminal
- potentially a test case to reproduce the problem
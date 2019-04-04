<div align="center">
  <img width=500px" src="https://framagit.org/gabylaunay/pyDSA/raw/master/branding/pyDSA_logo_python_text.svg"><br><br>
</div>


# PyDSAqt5: Graphical interface for drop shape analysis.


PyDSAqt5 is a graphical interface for [pyDSA](https://framagit.org/gabylaunay/pyDSA), a drop shape analyzer.

## Usage

Just fire up the GUI from the terminal (or anaconda console) with:

``pyDSAqt5``

## Mandatory screenshots

<img src="doc/screenshot1.png" alt="Import" width="300"/>

<img src="doc/screenshot2.png" alt="Import" width="300"/>

<img src="doc/screenshot3.png" alt="Import" width="300"/>

<img src="doc/screenshot4.png" alt="Import" width="300"/>



## Installation<a name="installation"></a>

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

### Winpython

You will need to download the following packages:

- [IMTreatment](https://framagit.org/gabylaunay/IMTreatment/-/archive/master/IMTreatment-master.zip)
- [pyDSA](https://framagit.org/gabylaunay/pyDSA/-/archive/master/pyDSA-master.zip)
- [pyDSAqt5](https://framagit.org/gabylaunay/pyDSAqt5/-/archive/master/pyDSAqt5-master.zip)

extract them, and install them (in order) with:

``python setup.py install``

## Updating

Because pyDSAqt5 does not follow (yet) a strict version strategy, you will have to uninstall and
reinstall the packages in order to make an update.

Uninstalling can be done using :

``pip uninstall IMTreatment pyDSA pyDSAqt5``
or
``conda uninstall IMTreatment pyDSA pyDSAqt5``

To reinstall, please follow the [above instructions](#installation).

## Documentation

pyDSAqt5 is designed to be simple and straightforward to use.
If you don't understand the effect of an option,
please refers to the inline documentation of [pyDSA](https://framagit.org/gabylaunay/pyDSA),
where all the features are documented in details.

## Issues and bugs

If pyDSAqt5 crashes or behaves abnormally, you can report [here](https://framagit.org/gabylaunay/pyDSAqt5/issues) or just send me an email at [gaby.launay@northumbria.ac.uk](mailto:gaby.launay@northumbria.ac.uk).
Any of the followings will greatly help me fix the issue:

- A description of the problem (as detailled as possible, for me to get it)
- The logs from the terminal
- A test case to reproduce the problem

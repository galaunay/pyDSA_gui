<div align="center">
  <img width=500px" src="https://framagit.org/gabylaunay/pyDSA/raw/master/branding/pyDSA_logo_text.svg"><br><br>
</div>


# pyDSA_gui: Graphical interface for drop shape analysis.


pyDSA_gui is a graphical interface for [pyDSA](https://framagit.org/gabylaunay/pyDSA), a drop shape analyzer.

## Usage

Just fire up the GUI from the terminal (or anaconda console) with:

``pyDSA_gui``

## Mandatory screenshots

<img src="doc/screenshot1.png" alt="Import" width="300"/>

<img src="doc/screenshot2.png" alt="Import" width="300"/>

<img src="doc/screenshot3.png" alt="Import" width="300"/>

<img src="doc/screenshot4.png" alt="Import" width="300"/>

## Documentation

pyDSA_gui is designed to be simple and straightforward to use.
If you don't understand the effect of an option,
please refers to the inline documentation of [pyDSA](https://framagit.org/gabylaunay/pyDSA),
where all the features are documented in details.

## Citing this software

If PyDSA have been usefull for you, please consider citing it:
```
Launay G. PyDSA: Drop shape analysis in Python, 2018-, https://framagit.org/gabylaunay/pyDSA [Online; accessed <today>].
```

bibtex entry:
``` bibtex
@Misc{,
  author =    {Gaby Launay},
  title =     {{PyDSA}: Drop shape analysis in {Python}},
  year =      {2018--},
  url = "https://framagit.org/gabylaunay/pyDSA",
  note = {[Online; accessed <today>]}
}
```


## Installation<a name="installation"></a>

### Linux

You will need [git](https://git-scm.com/) to be installed.

To install the dependencies that are not available on pipy, run:

``pip install 'git+https://framagit.org/gabylaunay/IMTreatment.git#egg=IMTreatment'``.

``pip install 'git+https://framagit.org/gabylaunay/pyDSA.git#egg=pyDSA'``.

Then install pyDSA_gui:

``pip install 'git+https://framagit.org/gabylaunay/pyDSA_gui.git#egg=pyDSA_gui'``

### Anaconda

Install git with:

``conda install git``

Install the dependencies:

``pip install git+https://framagit.org/gabylaunay/IMTreatment.git#egg=IMTreatment``.

``pip install git+https://framagit.org/gabylaunay/pyDSA.git#egg=pyDSA``.

And finally install pyDSA_gui:

``pip install git+https://framagit.org/gabylaunay/pyDSA_gui.git#egg=pyDSA_gui``

### Winpython

You will need to download the following packages:

- [IMTreatment](https://framagit.org/gabylaunay/IMTreatment/-/archive/master/IMTreatment-master.zip)
- [pyDSA_core](https://framagit.org/gabylaunay/pyDSA_core/-/archive/master/pyDSA_core-master.zip)
- [pyDSA_gui](https://framagit.org/gabylaunay/pyDSA_gui/-/archive/master/pyDSA_gui-master.zip)

extract them, and install them (in order) with:

``python setup.py install``

## Updating

Because pyDSA_gui does not follow (yet) a strict version strategy, you will have to uninstall and
reinstall the packages in order to make an update.

Uninstalling can be done using :

``pip uninstall IMTreatment pyDSA pyDSA_gui``
or
``conda uninstall IMTreatment pyDSA pyDSA_gui``

To reinstall, please follow the [above instructions](#installation).

## Issues and bugs

If pyDSA_gui crashes or behaves abnormally, you can report [here](https://framagit.org/gabylaunay/pyDSA_gui/issues) or just send me an email at [gaby.launay@northumbria.ac.uk](mailto:gaby.launay@northumbria.ac.uk).
Any of the followings will greatly help me fix the issue:

- A description of the problem (as detailled as possible, for me to get it)
- The logs from the terminal
- A test case to reproduce the problem

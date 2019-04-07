<div align="center">
  <img width=500px" src="https://framagit.org/gabylaunay/pyDSA_core/raw/master/branding/pyDSA_logo_text.svg"><br><br>
</div>


# pyDSA_gui: Graphical interface for drop shape analysis.


pyDSA_gui is a graphical interface for [pyDSA](https://framagit.org/gabylaunay/pyDSA_core), a drop shape analyzer.

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
please refers to the inline documentation of [pyDSA](https://framagit.org/gabylaunay/pyDSA_core),
where all the features are documented in details.

## Citing this software

If PyDSA_core have been usefull for you, please consider citing it:
```
Launay G. PyDSA_core: Drop shape analysis in Python, 2018-, https://framagit.org/gabylaunay/pyDSA_core [Online; accessed <today>].
```

bibtex entry:
``` bibtex
@Misc{,
  author =    {Gaby Launay},
  title =     {{PyDSA_core}: Drop shape analysis in {Python}},
  year =      {2018--},
  url = "https://framagit.org/gabylaunay/pyDSA_core",
  note = {[Online; accessed <today>]}
}
```


## Installation<a name="installation"></a>

### Pypi

``pip install pyDSA_core``

### Manually (Linux)

You will need [git](https://git-scm.com/) to be installed.

Then install pyDSA_gui:

``pip install 'git+https://framagit.org/gabylaunay/pyDSA_gui.git#egg=pyDSA_gui'``

### Manually (Anaconda)

Install git with:

``conda install git``

And then install pyDSA_gui:

``pip install git+https://framagit.org/gabylaunay/pyDSA_gui.git#egg=pyDSA_gui``

### Manually (Winpython)

You will need to download the following packages:

- [IMTreatment](https://framagit.org/gabylaunay/IMTreatment/-/archive/master/IMTreatment-master.zip)
- [pyDSA_core](https://framagit.org/gabylaunay/pyDSA_core/-/archive/master/pyDSA_core-master.zip)
- [pyDSA_gui](https://framagit.org/gabylaunay/pyDSA_gui/-/archive/master/pyDSA_gui-master.zip)

extract them, and install them (in order) with:

``python setup.py install``

## Updating

``pip install -U pydsa_gui``

## Issues and bugs

If pyDSA_gui crashes or behaves abnormally, you can report [here](https://framagit.org/gabylaunay/pyDSA_gui/issues) or just send me an email at [gaby.launay@northumbria.ac.uk](mailto:gaby.launay@northumbria.ac.uk).
Any of the followings will greatly help me fix the issue:

- A description of the problem (as detailled as possible, for me to get it)
- The logs from the terminal
- A test case to reproduce the problem

<div align="center">
  <img width=500px" src="https://framagit.org/gabylaunay/pyDSA_core/raw/master/branding/pyDSA_logo_text.svg"><br><br>
</div>


# Drop shape analysis software with graphical interface.


PyDSA is a software for drop shape analysis. It allows to measure the properties of droplets in contact with solids (contact angle, droplet volume, evaporation rate, displacement velocity, ...).
PyDSA is developed in Python and use Qt5 for it graphical interface.

## Installation<a name="installation"></a>

``pip install pyDSA_gui``

To update PyDSA, use:

``pip install -U pyDSA_gui``

## Usage

Just start PyDSA from the terminal (or anaconda console) with:

``pyDSA``

## Screenshots

Image scaling and pre-processing:

<img src="doc/screenshot1.png" alt="Import" width="300"/>

Droplet edge detection:

<img src="doc/screenshot2.png" alt="Import" width="300"/>

Droplet edge fitting:

<img src="doc/screenshot3.png" alt="Import" width="300"/>

Droplets properties evolution after full analysis:

<img src="doc/screenshot4.png" alt="Import" width="300"/>

## Documentation

PyDSA is designed to be simple and straightforward to use.
If you don't understand the effect of an option,
please refers to the inline documentation of [pyDSA_core](https://framagit.org/gabylaunay/pyDSA_core),
where all the features are documented in details.

## Citing this software

If PyDSA have been usefull for you, please consider citing it:
```
Launay G. PyDSA: Drop shape analysis in Python, 2018-, https://framagit.org/gabylaunay/pyDSA_core [Online; accessed <today>].
```

bibtex entry:
``` bibtex
@Misc{launay_pydsa_2018,
  author =    {Gaby Launay},
  title =     {{PyDSA}: Drop shape analysis in {Python}},
  year =      {2018--},
  url = "https://framagit.org/gabylaunay/pyDSA_core",
  note = {[Online; accessed <today>]}
}

```

## Issues and bugs

If pyDSA crashes or behaves abnormally, you can report [here](https://framagit.org/gabylaunay/pyDSA_gui/issues) or just send me an email at [gaby.launay@protonmail.com](mailto:gaby.launay@protonmail.com).
Any of the followings will greatly help me fix the issue:

- A description of the problem
- The logs from the terminal
- A test case to reproduce the problem

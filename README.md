<div align="center">
  <img width=500px" src="https://framagit.org/gabylaunay/pyDSA_core/raw/master/branding/pyDSA_logo_text.svg"><br><br>
</div>


# Drop shape analysis software.


PyDSA is a software for drop shape analysis.
It allows to measure the properties of droplets in contact with solids (contact angle, droplet volume, evaporation rate, displacement velocity, ...) through an intuitive interface.
PyDSA is developed in Python and use Qt5 for it graphical interface.

## Installation<a name="installation"></a>

``pip install pyDSA_gui``

To update PyDSA, use:

``pip install -U pyDSA_gui``

## Usage

Just start PyDSA from the terminal (or anaconda console) with:

``pyDSA``

## Screenshots
<div>
Image scaling and pre-processing:<br>
<a href="doc/screenshot1.png">
<img src="doc/screenshot1.png" alt="Import" width="300"/>
</a>
</div>
<div>
<br>
Droplet edge detection:<br>
<a href="doc/screenshot2.png">
<img src="doc/screenshot2.png" alt="Import" width="300"/>
</a>
</div>
<div>
<br>
Droplet edge fitting:<br>
<a href="doc/screenshot3.png">
<img src="doc/screenshot3.png" alt="Import" width="300"/>
</a>
</div>
<div>
<br>
Droplets properties evolution after full analysis:<br>
<a href="doc/screenshot4.png">
<img src="doc/screenshot4.png" alt="Import" width="300"/>
</a>
</div>

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

PyDSA is hosted on [Framagit](https://framagit.org/gabylaunay/pyDSA_gui).
If PyDSA crashes or behaves abnormally, just send me an email at [gaby.launay@protonmail.com](mailto:gaby.launay@protonmail.com).
Any of the followings will greatly help me fix the issue:

- A description of the problem
- The logs from the terminal
- A test case to reproduce the problem

#!/bin/bash

bumpversion $@
python3 -m pip install --upgrade setuptools wheel twine
rm -rf dist
python3 setup.py sdist bdist_wheel
twine upload dist/*
git push
git push --tags

#! /usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from setuptools import setup, find_packages

CURRENT_DIR = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(CURRENT_DIR, "README.md"), "r") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="wgraph",
    version="0.0.1",
    description="Parsing Wiktionary Etymology Data",
    long_description=LONG_DESCRIPTION,
    url="https://github.com/remusao/wgraph",
    author="Rémi",
    license="MIT",
    packages=find_packages(),
    install_requires=["docopt", "tqdm"],
    extras_require={"dev": ["black", "mypy", "profiling", "pylint", "pre-commit"]},
    entry_points={
        "console_scripts": [
            "parse = wgraph.parse_wikidata:main",
            "distance = wgraph.distance:main",
        ]
    },
)

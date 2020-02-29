#! /usr/bin/env python3


# --- import -------------------------------------------------------------------------------------


import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(here, fname)).read()


here = os.path.abspath(os.path.dirname(__file__))

extra_files = {"attune": ["VERSION"]}

with open(os.path.join(here, "attune", "VERSION")) as version_file:
    version = version_file.read().strip()


# --- setup function -----------------------------------------------------------------------------


setup(
    name="attune",
    packages=find_packages(exclude=("tests", "tests.*")),
    package_data=extra_files,
    python_requires=">=3.5",
    install_requires=["WrightTools>=3.2.5", "numpy", "scipy", "matplotlib", "tidy_headers"],
    extras_require={
        "dev": ["black", "pre-commit"],
        "docs": ["sphinx-gallery>0.3.0", "sphinx", "sphinx-rtd-theme"],
    },
    version=version,
    description="Tools for tuning optical parametric amplifiers and multidimensional spectrometers.",
    long_description=read("README.rst"),
    author="Blaise Thompson",
    author_email="blaise@untzag.com",
    license="MIT",
    url="https://github.com/wright-group/attune",
    keywords="spectroscopy science multidimensional visualization",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering",
    ],
)

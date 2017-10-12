#! /usr/bin/env python


# --- import -------------------------------------------------------------------------------------


import os
from setuptools import setup, find_packages


# --- functions ----------------------------------------------------------------------------------


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


# ---- objects -----------------------------------------------------------------------------------


here = os.path.abspath(os.path.dirname(__file__))


extra_files = []
extra_files.append(os.path.join(here, 'CONTRIBUTORS'))
extra_files.append(os.path.join(here, 'LICENSE'))
extra_files.append(os.path.join(here, 'README.rst'))
extra_files.append(os.path.join(here, 'requirements.txt'))
extra_files.append(os.path.join(here, 'VERSION'))
extra_files.append(os.path.join(here, 'WrightTools', 'client_secrets.json'))


with open(os.path.join(here, 'requirements.txt')) as f:
    required = f.read().splitlines()


with open(os.path.join(here, 'VERSION')) as version_file:
    version = version_file.read().strip()


# --- setup function -----------------------------------------------------------------------------


setup(
    name='attune',
    packages=find_packages(),
    package_data={'': extra_files},
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    install_requires=required,
    extras_require={'docs': ['sphinx-gallery>=0.1.9']},
    version=version,
    description='Tools for tuning optical parametric amplifiers and multidimensional spectrometers.',
    author='Blaise Thompson',
    author_email='blaise@untzag.com',
    license='MIT',
    url='https://github.com/wright-group/attune',
    keywords='spectroscopy science multidimensional visualization',
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Topic :: Scientific/Engineering']
)

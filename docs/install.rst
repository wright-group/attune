.. _install:


Installation
============

``attune`` requires Python 3.6 or newer.

conda-forge
-----------

Conda_ is a multilingual package/environment manager.
It seamlessly handles non-Python library dependencies which many scientific Python tools rely upon.
Conda is recommended, especially for Windows users.
If you don't have Python yet, start by `installing Anaconda`_ or `miniconda`_.

`conda-forge`_ is a community-driven conda channel. `conda-forge contains an attune feedstock`_.

.. code-block:: bash

    conda config --add channels conda-forge
    conda install attune

To upgrade:

.. code-block:: bash

    conda update attune

pip
---

pip_ is Python's official package manager. `attune is hosted on PyPI`_.


.. code-block:: bash

    pip install attune

To upgrade:

.. code-block:: bash

    pip install attune --upgrade

.. _Conda: https://conda.io/docs/intro.html
.. _installing Anaconda: https://www.continuum.io/downloads
.. _conda-forge: https://conda-forge.org/
.. _conda-forge contains an attune feedstock: https://github.com/conda-forge/attune-feedstock
.. _miniconda: https://conda.io/miniconda.html
.. _pip: https://pypi.python.org/pypi/pip
.. _attune is hosted on PyPI: https://pypi.org/project/attune/

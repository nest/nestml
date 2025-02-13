Installing NESTML
=================

Please note that only Python 3.9 (and later versions) are supported. The instructions below assume that ``python`` is aliased to or refers to ``python3``, and ``pip`` to ``pip3``.

Installing the latest release from PyPI
---------------------------------------

The easiest way to install NESTML is to use the `Python Package Index (PyPI) <https://pypi.org>`_. This requires the Python package management system ``pip`` to be installed. In Ubuntu, Mint and Debian Linux you can install ``pip`` as follows:

.. code-block:: bash

   sudo apt install python3-pip

NESTML can then be installed into your local user directory via:

.. code-block:: bash

   pip install nestml


Installing the latest release from PPA (Linux)
----------------------------------------------

NESTML can be installed via the ``apt`` package manager. This requires superuser (sudo) access. First, add the NEST PPA:

.. code-block:: bash

   sudo add-apt-repository ppa:nest-simulator/nest

Then update the index and install the necessary packages:

.. code-block:: bash

   sudo apt update
   sudo apt install nest python3-nestml
   python3 -m pip install --upgrade odetoolbox pygsl antlr4-python3-runtime==4.10

Before running NEST or NESTML, make sure the correct environment variables are set by running the following command:

.. code-block:: bash

   source /usr/bin/nest_vars.sh


Installing the latest development version from GitHub
-----------------------------------------------------

To obtain the latest development version, clone directly from the master branch of the GitHub repository:

.. code-block:: bash

   git clone https://github.com/nest/nestml


Install into your local user directory using:

.. code-block:: bash

   cd nestml
   python setup.py install --user


.. Attention::

   When using the latest development version, you may also need the development version of ODE-toolbox. It can be installed by running:

   .. code-block:: bash

      pip install git+https://github.com/nest/ode-toolbox


Testing
-------

After installation, correct operation can be tested by:

.. code-block:: bash

   python setup.py test


Installation with conda (with NEST simulator)
---------------------------------------------

In preparation, `create a conda environment with NEST <https://nest-simulator.readthedocs.io/en/stable/installation/index.html>`_, and install some additional dependencies.

.. note::

   We recommend using `miniforge <https://github.com/conda-forge/miniforge>`_ or `micromamba <https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html>`_ in place of Anaconda/miniconda as they have some advantages when installing in larger environments.

Please make sure to have the latest conda version installed and to create a new environment with the command below, i.e. installing all packages together at the start versus installing one by one.

.. code-block:: bash

   conda create --name <env_name>
   conda activate <env_name>
   conda install -c conda-forge nest-simulator ipython cxx-compiler boost boost-cpp libboost cmake make
   pip install nestml

Alternatively, NEST can also be installed from source in a conda environment. The instructions can be found `here <https://nest-simulator.readthedocs.io/en/stable/installation/condaenv_install.html#condaenv>`_.

After installing NESTML, the neuron and synapse models can be found in the path ``$HOME/miniforge3/envs/<env_name>/models`` and the tutorial notebooks can be found under ``$HOME/miniforge3/envs/<env_name>/doc/tutorials``.
For more information on how to run NESTML, please refer to `Running NESTML <https://nestml.readthedocs.io/en/latest/running/index.html>`_.


Docker installation
-------------------

NESTML is installed as part of the official NEST Simulator `Docker <https://docker.io/>`_ image.

For detailed instructions, please see https://nest-simulator.readthedocs.io/en/latest/installation/index.html.

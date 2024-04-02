Installing NESTML
=================

Please note that only Python 3.8 (and later versions) are supported. The instructions below assume that ``python`` is aliased to or refers to ``python3``, and ``pip`` to ``pip3``.

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


Anaconda installation
---------------------

In preparation, `create a conda environment with NEST <https://nest-simulator.readthedocs.io/en/stable/installation/index.html>`_, and install some additional dependencies:

.. code-block:: bash

   conda create --name wnestml
   conda activate wnestml
   conda install -c conda-forge nest-simulator ipython cxx-compiler pyqt wxpython boost boost-cpp libboost
   pip install nestml

Test the path to ``c++``:

.. code-block:: bash

   which c++
   # '/home/graber/miniconda3/envs/wnestml/bin/c++'

Edit ``nest-config`` and correct the entry under ``--compiler`` with the output returned by ``which c++``:

.. code-block:: bash

   nano /home/graber/miniconda3/envs/wnestml/bin/nest-config

macOS users must in addition replace the ``-fopenmp=libomp`` entries with ``-Xclang -fopenmp`` under both ``--cflags`` and ``--libs`` in the ``nest-config``.

Now set the correct paths and start ``ipython``:

.. code-block:: bash

   export PYTHONPATH=$PYTHONPATH:/home/graber/miniconda3/envs/wnestml/lib/python3.7/site-packages
   export LD_LIBRARY_PATH=/tmp/nestml-component
   ipython

The corresponding paths in ``ipython`` are:

.. code-block:: python

   from pynestml.frontend.pynestml_frontend import generate_nest_target
   generate_nest_target(input_path="/home/graber/work/nestml/doc/tutorial/izhikevich_solution.nestml",
                        target_path="/tmp/nestml-component",
                        logging_level="INFO")


Docker installation
-------------------

NESTML is installed as part of the official NEST Simulator `Docker <https://docker.io/>`_ image.

For detailed instructions, please see https://nest-simulator.readthedocs.io/en/latest/installation/index.html.

Installing NESTML
=================

Please note that only Python 3 is supported. The instructions below assume that ``python`` is aliased to or refers to ``python3``, and ``pip`` to ``pip3``.

Installing the latest release from PyPI
---------------------------------------

.. Attention:: As NESTML is currently getting close to its version 4.0 release, we recommend using the development version (see below under :ref:`Installing the latest development version from GitHub`).

The easiest way to install NESTML is to use the `Python Package Index (PyPI) <https://pypi.org>`_. This requires the Python package management system ``pip`` to be installed. In Ubuntu, Mint and Debian Linux you can install ``pip`` as follows:

.. code-block:: bash

   sudo apt install python3-pip

NESTML can then be installed into your local user directory via:

.. code-block:: bash

   pip install nestml


Installing the latest development version from GitHub
-----------------------------------------------------

To obtain the latest development version, clone directly from the master branch of the GitHub repository:

.. code-block:: bash

   git clone https://github.com/nest/nestml


Install into your local user directory using:

.. code-block:: bash

   cd nestml
   python setup.py install --user


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
   conda install -c conda-forge nest-simulator ipython cxx-compiler pyqt wxpython
   pip install nestml

Test the path to ``c++``:

.. code-block:: bash

   which c++ 
   # '/home/graber/miniconda3/envs/wnestml/bin/c++'

Edit ``nest-config`` and correct the entry under ``--compiler`` with the output returned by ``which c++``:

.. code-block:: bash

   nano /home/graber/miniconda3/envs/wnestml/bin/nest-config

Now set the correct paths and start ``ipython``:

.. code-block:: bash

   export PYTHONPATH=$PYTHONPATH:/home/graber/miniconda3/envs/wnestml/lib/python3.7/site-packages
   export LD_LIBRARY_PATH=/tmp/nestml-component
   ipython

The corresponding paths in ``ipython`` are:

.. code-block:: python

   from pynestml.frontend.pynestml_frontend import to_nest, install_nest
   to_nest(input_path="/home/graber/work/nestml/doc/tutorial/izhikevich_solution.nestml",
           target_path="/tmp/nestml-component",
           logging_level="INFO")
   install_nest("/tmp/nestml-component", "/home/graber/miniconda3/envs/wnestml/") 

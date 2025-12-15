NEST GPU target
---------------

*NESTML features supported:* :doc:`neurons </nestml_language/neurons_in_nestml>`

Introduction
~~~~~~~~~~~~

NEST GPU is a GPU-MPI library for simulation of large-scale networks of spiking neurons, written in C++ and CUDA-C++ programming languages [Gol21]_.

NESTML code generation support for NEST GPU currently covers neuron models with linear dynamics that can be solved with propagators, as well as neurons that require a numeric solver, which is implemented with a Runge-Kutta-Fehlberg (RK45) solver in NEST GPU.

Generating code
~~~~~~~~~~~~~~~

1. Install NEST GPU. Follow the installation steps in the NEST GPU `docs <https://nest-gpu.readthedocs.io/en/latest/installation/index.html>`_.

2. Create an environment variable ``NEST_GPU`` that points to the NEST GPU source code. For example,

   .. code-block:: bash

      export NEST_GPU=$HOME/nest-gpu

3. Install NESTML in ``$HOME/nestml``. Install the NESTML verison with the `NEST GPU support <https://github.com/nest/nestml/pull/860>`_. The NESTML installation instructions can be found :doc:`here <../installation>`.

4. Run the test from NESTML that generates and compiles the code for NEST GPU.

   .. code-block:: bash

      pytest -s tests/nest_gpu_tests/nest_gpu_code_generator_test.py -k "test_nest_gpu_code_generator_analytic"

5. Run the script for the single neuron simuation.

   .. code-block:: bash

      cd extras/nest_gpu/examples/iaf_psc_exp
      python example_iaf_psc_exp.py

References
~~~~~~~~~~

.. [Gol21] Golosio et al., Fast Simulations of Highly-Connected Spiking Cortical Models Using GPUs, 2021, https://doi.org/10.3389/fncom.2021.627620
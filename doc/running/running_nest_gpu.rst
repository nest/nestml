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

3. Install NESTML in ``$HOME/nestml``. The NESTML installation instructions can be found :doc:`here <../installation>`.

4. Run the test from NESTML that generates and compiles the code for the neuron models with analytic and numeric solver for NEST GPU, and performs single-neuron simulations. The tests can be found in the directory `tests/nest_gpu_tests <https://github.com/nest/nestml/tree/main/tests/nest_gpu_tests>`_

   .. code-block:: bash

      # Test for a neuron model with analytic solver
      pytest -s tests/nest_gpu_tests/test_nest_gpu_code_generator_analytic.py

      # Test for neuron models with numeric solver
      pytest -s tests/nest_gpu_tests/test_nest_gpu_code_generator_numeric.py


Models with numeric solvers
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Neuron models that require numeric solvers use Runge-Kutta Fehlberg (``rk45``) method to solve the ODEs. The minimum step size ``h_min_rel`` and initial integration step ``h0_rel`` are variables set inside the model during code generation. They can also be modified at runtime as parameters of the model instance.

   .. code-block::

    neuron = ngpu.Create("aeif_cond_alpha_neuron_nestml", 1)
    ngpu.SetStatus(neuron, {"h_min_rel": 0.01, "h0_rel": 0.1})


References
~~~~~~~~~~

.. [Gol21] Golosio et al., Fast Simulations of Highly-Connected Spiking Cortical Models Using GPUs, 2021, https://doi.org/10.3389/fncom.2021.627620
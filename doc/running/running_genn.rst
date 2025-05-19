GeNN target
-----------

*NESTML features supported:* :doc:`neurons </nestml_language/neurons_in_nestml>`

Introduction
~~~~~~~~~~~~

GeNN is a GPU-enhanced Neuronal Network simulation environment based on code generation for Nvidia CUDA [Yav2016]_ [GeNNGitHub]_ [GeNNRtD]_.

NESTML code generation support for GeNN is currently limited to neurons with linear dynamics that can be solved with propagators, as well as neurons that require a numeric solver, which for GeNN is implemented (in the neuron code templates) as a forward Euler solver.

Please see the unit tests in https://github.com/nest/nestml/tree/master/tests/genn_tests for usage examples.


Generating code
~~~~~~~~~~~~~~~

1. Install GeNN

2. Run the tests:

   .. code-block:: bash

      python3 -m pytest tests/genn_tests

   These will generate rastergrams for a simple, single-neuron example in ``/tmp``, for both the Izhikevich and the integrate-and-fire model with an exponentially decaying postsynaptic kernel.


References
~~~~~~~~~~

.. [Yav2016] Yavuz, E., Turner, J. and Nowotny, T. (2016) GeNN: a code generation framework for accelerated brain simulations. Scientific Reports 6, 18854.

.. [GenGitHub] https://github.com/genn-team/genn/

.. [GenRtD] https://genn-team.github.io/

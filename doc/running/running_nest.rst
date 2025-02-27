NEST Simulator target
=====================

*NESTML features supported:* :doc:`neurons </nestml_language/neurons_in_nestml>`, :doc:`synapses </nestml_language/synapses_in_nestml>`, :ref:`vectors <Vectors>`, :ref:`delay differential equations <Delay Differential Equations>`, :ref:`guards <Guards>`

Generates code for NEST Simulator. For a list of supported versions, see :ref:`Compatibility with different versions of NEST <nest_versions_compatibility>`.

After NESTML completes, the NEST extension module (by default called ``"nestmlmodule"``) can either be statically linked into NEST (see `Writing an extension module <https://nest-extension-module.readthedocs.io/>`_), or loaded dynamically using the ``Install`` API call in Python.

.. note::

   Several code generator options are available; for an overview see :class:`pynestml.codegeneration.nest_code_generator.NESTCodeGenerator`.


Simulation loop
---------------

Note that NEST Simulator uses a hybrid integration strategy [Hanuschkin2010]_; see :numref:`fig_integration_order`, panel A for a graphical depiction.

At the start of a timestep, the value is the one "just before" the update due to incoming spikes. Then, the code is run corresponding to the NESTML ``update`` block, which makes appropriate calls to integrate the necessary ODEs. After that, incoming spikes are processed, that is, the code corresponding to ``onReceive`` blocks is run and the values of variables corresponding to convolutions are updated.


Event-based updating of synapses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The synapse is allowed to contain an ``update`` block. Statements in the ``update`` block are executed whenever the internal state of the synapse is updated from one timepoint to the next; these updates are typically triggered by incoming spikes. The NESTML ``resolution()`` function will return the time that has elapsed since the last event was handled.

Synapses in NEST are not allowed to have any nonlinear time-based internal dynamics (ODEs). This is due to the fact that synapses are, unlike nodes, not updated on a regular time grid. Linear ODEs are allowed, because they admit an analytical solution, which can be updated in a single step from the previous event time to the current event time. However, nonlinear dynamics are not allowed because they would require a numeric solver evaluating the dynamics on a regular time grid.

If ODE-toolbox is not successful in finding the propagator solver to a system of ODEs that is, however, solvable, the propagators may be entered "by hand" in the ``update`` block of the model. This block may contain any series of statements to update the state of the system from the current timestep to the next, for example, multiplications of state variables by the propagators.


Setting and retrieving model properties
---------------------------------------

-  All variables in the ``state`` and ``parameters`` blocks are added to the status dictionary of the neuron.
-  Values can be set using the PyNEST API call ``node_collection.<variable> = <value>`` where ``<variable>`` is the name of the corresponding NESTML variable.
-  Values can be read using the PyNEST API call ``node_collection.<variable>``. This will return the value of the corresponding NESTML variable.


Recording values with devices
-----------------------------

All values in the ``state`` block are recordable by a ``multimeter`` in NEST.


Solver selection
----------------

Currently, there is support for GSL, forward Euler, and exact integration. ODEs that can be solved analytically are integrated to machine precision from one timestep to the next. To allow more precise values for analytically solvable ODEs *within* a timestep, the same ODEs are evaluated numerically by the GSL solver. In this way, the long-term dynamics obeys the "exact" equations, while the short-term (within one timestep) dynamics is evaluated to the precision of the numerical integrator.

In the case that the model is solved with the GSL integrator, desired absolute error of an integration step can be adjusted with the ``gsl_error_tol`` parameter in a ``SetStatus`` call. The default value of ``gsl_error_tol`` is ``1e-3``.


Manually building the extension module
--------------------------------------

Sometimes it can be convenient to directly edit the generated code. To manually build and install the NEST extension module, go into the target directory and run:

.. code-block:: bash

   cmake -Dwith-nest=<nest_install_dir>/bin/nest-config .
   make all
   make install

where ``<nest_install_dir>`` is the installation directory of NEST (e.g. ``/home/nest/work/nest-install``).


Generating code for synapses
----------------------------

In NEST, synapses derive from the C++ class ``Connection``, whereas neurons derive from ``Node``. To make it clear to the code generator whether a given NESTML model is a neuron or synapse model, the code generator option ``synapse_models`` can be used. If the model name ends with the string ``"synapse"`` (for instance, ``"stdp_synapse"``), the model is also interpreted as a synapse.


Gap junctions (electrical synapses)
-----------------------------------

Each neuron model can be endowed with gap junctions. The model does not need to be (necessarily) modified itself, but additional flags are passed during code generation that identify which model variables correspond to the membrane potential and the gap junction current. For instance, the code generator options can look as follows:

.. code-block:: python

   "gap_junctions": {
       "enable": True,
       "membrane_potential_variable": "V_m",
       "gap_current_port": "I_gap"
   }

For a full example, please see `test_gap_junction.py <https://github.com/nest/nestml/blob/master/tests/nest_tests/test_gap_junction.py>`_.


Multiple input ports in NEST
----------------------------

See :ref:`Multiple input ports` to specify multiple input ports in a neuron.

After generating and building the model code, a ``receptor_type`` entry is available in the status dictionary, which maps port names to numeric port indices in NEST. The receptor type can then be selected in NEST during `connection setup <https://nest-simulator.readthedocs.io/en/latest/synapses/connection_management.html#receptor-types>`_:

.. code-block:: python

   neuron = nest.Create("iaf_psc_exp_multisynapse_neuron_nestml")

   receptor_types = nest.GetStatus(neuron, "receptor_types")[0]

   sg = nest.Create("spike_generator", params={"spike_times": [20., 80.]})
   nest.Connect(sg, neuron, syn_spec={"receptor_type" : receptor_types["SPIKES_1"], "weight": 1000.})

   sg2 = nest.Create("spike_generator", params={"spike_times": [40., 60.]})
   nest.Connect(sg2, neuron, syn_spec={"receptor_type" : receptor_types["SPIKES_2"], "weight": 1000.})

   sg3 = nest.Create("spike_generator", params={"spike_times": [30., 70.]})
   nest.Connect(sg3, neuron, syn_spec={"receptor_type" : receptor_types["SPIKES_3"], "weight": 500.})

Note that in multisynapse neurons, receptor ports are numbered starting from 1.

We furthermore wish to record the synaptic currents ``I_kernel1``, ``I_kernel2`` and ``I_kernel3``. During code generation, one buffer is created for each combination of (kernel, spike input port) that appears in convolution statements. These buffers are named by joining together the name of the kernel with the name of the spike buffer using (by default) the string "__X__". The variables to be recorded are thus named as follows:

.. code-block:: python

   mm = nest.Create('multimeter', params={'record_from': ['I_kernel1__X__spikes_1',
                                                          'I_kernel2__X__spikes_2',
                                                          'I_kernel3__X__spikes_3'],
                                          'interval': .1})
   nest.Connect(mm, neuron)

The output shows the currents for each synapse (three bottom rows) and the net effect on the membrane potential (top row):

.. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/fig/nestml-multisynapse-example.png
   :alt: NESTML multisynapse example waveform traces

For a full example, please see `iaf_psc_exp_multisynapse.nestml <https://github.com/nest/nestml/blob/master/tests/nest_tests/resources/iaf_psc_exp_multisynapse.nestml>`_ for the full model and ``test_multisynapse`` in `tests/nest_tests/nest_multisynapse_test.py <https://github.com/nest/nestml/blob/master/tests/nest_tests/nest_multisynapse_test.py>`_ for the corresponding test harness that produced the figure above.


Multiple input ports with vectors in NEST
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See :ref:`Multiple input ports with vectors` for an example with input ports defined as vectors.

Each connection in NEST is denoted by a receiver port or ``rport`` number which is an integer that starts with 0. All default connections in NEST have the ``rport`` 0. NESTML routes the spikes with ``excitatory`` and ``inhibitory`` qualifiers into separate input buffers, whereas NEST identifies them with the same ``rport`` number.

During the code generation for NEST, NESTML maintains an internal mapping between NEST ``rports`` and NESTML input ports. A list of port names defined in a model and their corresponding ``rport`` numbers can be queried from the status dictionary using the NEST API. For neurons with multiple input ports, the ``receptor_type`` values in the ``nest.Connect()`` call start from 1 as the default ``receptor_type`` 0 is excluded to avoid any accidental connections.

For the example mentioned :ref:`here <Multiple input ports with vectors>`, the ``receptor_types`` can be queried as shown below:

.. code-block:: python

   neuron = nest.Create("multi_synapse_vectors")
   receptor_types = nest.GetStatus(neuron, "receptor_types")

The name of the receptors of the input ports are denoted by suffixing the ``vector index`` to the port name. For instance, the receptor name for ``foo[0]`` would be ``FOO_0``.

The above code querying for ``receptor_types`` gives a list of port names and NEST ``rport`` numbers as shown below:

.. list-table::
   :header-rows: 1

   * - Input port name
     - NEST ``rport``
   * - AMPA_spikes
     - 1
   * - GABA_spikes
     - 1
   * - NMDA_spikes
     - 2
   * - FOO_0
     - 3
   * - FOO_1
     - 4
   * - EXC_SPIKES_0
     - 5
   * - EXC_SPIKES_1
     - 6
   * - EXC_SPIKES_2
     - 7
   * - INH_SPIKES_0
     - 5
   * - INH_SPIKES_1
     - 6
   * - INH_SPIKES_2
     - 7

For a full example, please see `iaf_psc_exp_multisynapse_vectors.nestml <https://github.com/nest/nestml/blob/master/tests/nest_tests/resources/iaf_psc_exp_multisynapse_vectors.nestml>`_ for the neuron model and ``test_multisynapse_with_vector_input_ports`` in `tests/nest_tests/nest_multisynapse_test.py <https://github.com/nest/nestml/blob/master/tests/nest_tests/nest_multisynapse_test.py>`_ for the corresponding test.


Generating code
---------------

Output event attributes
~~~~~~~~~~~~~~~~~~~~~~~

In neuron models, no spike event attributes are supported.

In synapse models, precisely two spike event attributes are supported: a synaptic weight (as a real number) and a synaptic (dendritic) delay (in milliseconds).


Generating code for plastic synapses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When NESTML is invoked to generate code for plastic synapses, the code generator needs to know which neuron model the synapses will be connected to, so that it can generate fast C++ code for the neuron and the synapse that is mutually dependent at runtime. These pairs can be specified as a list of two-element dictionaries of the form :code:`{"neuron": "neuron_model_name", "synapse": "synapse_model_name"}`, for example:

.. code-block:: python

   generate_target(...,
                   codegen_opts={...,
                                 "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_dend",
                                                           "synapse": "third_factor_stdp"}]})

Additionally, if the synapse requires it, specify the ``"post_ports"`` entry to connect the input port on the synapse with the right variable of the postsynaptic neuron:

.. code-block:: python

   generate_target(...,
                   codegen_opts={...,
                                 "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_dend",
                                                           "synapse": "third_factor_stdp",
                                                           "post_ports": ["post_spikes",
                                                                          ["I_post_dend", "I_dend"]]}]})

This specifies that the neuron ``iaf_psc_exp_dend`` has to be generated paired with the synapse ``third_factor_stdp``, and that the input ports ``post_spikes`` and ``I_post_dend`` in the synapse are to be connected to the postsynaptic partner. For the ``I_post_dend`` input port, the corresponding variable in the (postsynaptic) neuron is called ``I_dend``.

Simulation of volume-transmitted neuromodulation in NEST can be done using "volume transmitter" devices [5]_. These are event-based and should correspond to a "spike" type input port in NESTML. The code generator options keyword ``"vt_ports"`` can be used here.

.. code-block:: python

   generate_target(...,
                   codegen_opts={...,
                                 "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_dend",
                                                           "synapse": "third_factor_stdp",
                                                            "vt_ports": ["dopa_spikes"]}]})


Third-factor plasticity
~~~~~~~~~~~~~~~~~~~~~~~

When a continuous-time input port is defined in the synapse model which is connected to a postsynaptic neuron, a corresponding buffer is allocated in each neuron which retains the recent history of the needed state variables. Two options are available for how the buffer is implemented: a "continuous-time" based buffer, or a spike-based buffer (see the NEST code generator option ``continuous_state_buffering_method`` on https://nestml.readthedocs.io/en/latest/pynestml.codegeneration.html#pynestml.codegeneration.nest_code_generator.NESTCodeGenerator).

By default, the "continuous-time" based buffer is selected. This covers the most general case of different synaptic delay values and a discontinuous third-factor signal. The implementation corresponds to the event-based update scheme in Fig. 4b of [Stapmanns2021]_. There, the authors observe that the storage and management of such a buffer can be expensive in terms of memory and runtime. In each time step, the value of the current dendritic current (or membrane potential, or other third factor) is appended to the buffer. The maximum length of the buffer depends on the maximum inter-spike interval of any of the presynaptic neurons.

As a computationally more efficient alternative, a spike-based buffer can be selected. In this case, the third factor is not stored every timestep, but only upon the occurrence of postsynaptic (somatic) spikes. Because of the existence of a nonzero dendritic delay, the time at which the somatic spike is observed at the synapse is delayed, and the time at which the third factor is sampled should match the time of the spike at the synapse, rather than the soma. When the spike-based buffering method is used, the dendritic delay is therefore ignored, because the third factor is sampled instead at the time of the somatic spike.




Dendritic delay and synaptic weight
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In NEST, all synapses are expected to specify a nonzero dendritic delay, that is, the delay between arrival of a spike at the dendritic spine and the time at which its effects are felt at the soma (or conversely, the delay between a somatic action potential and the arrival at the dendritic spine due to dendritic backpropagation). As delays and weights are hard-wired into the NEST C++ base classes for the NESTML synapse classes, special annotations must be made in the NESTML model to indicate which state variables or parameters correspond to weight and delay. To indicate the correspondence, use the code generator options ``delay_variable`` and ``weight_variable``. For example, given the following model:

.. code:: nestml

   model my_synapse:
       state:
           w real = 1.

       parameters:
           dend_delay ms = 1 ms

the variables might be specified as:

.. code-block:: python

   generate_target(...,
                   codegen_opts={...,
                                 "delay_variable": {"my_synapse": "dend_delay"},
                                 "weight_variable": {"my_synapse": "w"}})


Custom templates
~~~~~~~~~~~~~~~~

See :ref:`Running NESTML with custom templates`.


.. _nest_versions_compatibility:

Compatibility with different versions of NEST
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To generate code that is compatible with particular versions of NEST Simulator, the code generator option  ``nest_version`` can be used. The option value is given as a string that corresponds to a git tag or git branch name. The following values are supported:

- The default is the empty string, which causes the NEST version to be automatically identified from the ``nest`` Python module.
- ``"master"``: Latest NEST GitHub master branch version (https://github.com/nest/nest-simulator/).
- ``"v2.20.2"``: Latest NEST 2 release.
- ``"v3.0"``, ``"v3.1"``, ``"v3.2"``, etc.: NEST 3 release versions.

For a list of the corresponding NEST Simulator repository tags, please see https://github.com/nest/nest-simulator/tags.


Random numbers
--------------

In case random numbers are needed inside the synapse, the random number generator belonging to the postsynaptic target is used.


References
----------

.. [Hanuschkin2010] Alexander Hanuschkin and Susanne Kunkel and Moritz Helias and Abigail Morrison and Markus Diesmann. A General and Efficient Method for Incorporating Precise Spike Times in Globally Time-Driven Simulations. Frontiers in Neuroinformatics, 2010, Vol. 4

.. [Stapmanns2021] Jonas Stapmanns, Jan Hahne, Moritz Helias, Matthias Bolten, Markus Diesmann and David Dahmen. Event-Based Update of Synapses in Voltage-Based Learning Rules. Frontiers in Neuroinformatics, Volume 15, 10 June 2021

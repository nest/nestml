NEST Simulator target
---------------------

*NESTML features supported:* :doc:`neurons </nestml_language/neurons_in_nestml>`, :doc:`synapses </nestml_language/synapses_in_nestml>`, :ref:`vectors <Vectors>`, :ref:`delay differential equations <Delay Differential Equations>`, :ref:`guards <Guards>`

After NESTML completes, the NEST extension module (by default called ``"nestmlmodule"``) can either be statically linked into NEST (see `Writing an extension module <https://nest-extension-module.readthedocs.io/>`_), or loaded dynamically using the ``Install`` API call in Python.

Parameters, internals and state variables can be set and read by the user using ``nest.SetStatus()`` and ``nest.GetStatus()``.

Code generation options
~~~~~~~~~~~~~~~~~~~~~~~

Several code generator options are available; for an overview see :class:`pynestml.codegeneration.nest_code_generator.NESTCodeGenerator`.


Manually building the extension module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes it can be convenient to directly edit the generated code. To manually build and install the NEST extension module, go into the target directory and run:

.. code-block:: bash

   cmake -Dwith-nest=<nest_install_dir>/bin/nest-config .
   make all
   make install

where ``<nest_install_dir>`` is the installation directory of NEST (e.g. ``/home/nest/work/nest-install``).


Custom templates
~~~~~~~~~~~~~~~~

See :ref:`Running NESTML with custom templates`.


Gap junctions (electrical synapses)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each neuron model can be endowed with gap junctions. The model does not need to be (necessarily) modified itself, but additional flags are passed during code generation that identify which model variables correspond to the membrane potential and the gap junction current. For instance, the code generator options can look as follows:

.. code-block:: python

   "gap_junctions": {
       "enable": True,
       "membrane_potential_variable": "V_m",
       "gap_current_port": "I_gap"
   }

For a full example, please see `test_gap_junction.py <https://github.com/nest/nestml/blob/master/tests/nest_tests/test_gap_junction.py>`_.


Multiple input ports in NEST
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

The name of the receptors of the input ports are denoted by suffixing the ``vector index + 1`` to the port name. For instance, the receptor name for ``foo[0]`` would be ``FOO_1``.

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
   * - FOO_1
     - 3
   * - FOO_2
     - 4
   * - EXC_SPIKES_1
     - 5
   * - EXC_SPIKES_2
     - 6
   * - EXC_SPIKES_3
     - 7
   * - INH_SPIKES_1
     - 5
   * - INH_SPIKES_2
     - 6
   * - INH_SPIKES_3
     - 7

For a full example, please see `iaf_psc_exp_multisynapse_vectors.nestml <https://github.com/nest/nestml/blob/master/tests/nest_tests/resources/iaf_psc_exp_multisynapse_vectors.nestml>`_ for the neuron model and ``test_multisynapse_with_vector_input_ports`` in `tests/nest_tests/nest_multisynapse_test.py <https://github.com/nest/nestml/blob/master/tests/nest_tests/nest_multisynapse_test.py>`_ for the corresponding test.

Compatibility with different versions of NEST
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To generate code that is compatible with particular versions of NEST Simulator, the code generator option  ``nest_version`` can be used. The option value is given as a string that corresponds to a git tag or git branch name. The following values are supported:

- The default is the empty string, which causes the NEST version to be automatically identified from the ``nest`` Python module.
- ``"master"``: Latest NEST GitHub master branch version (https://github.com/nest/nest-simulator/).
- ``"v2.20.2"``: Latest NEST 2 release.
- ``"v3.0"``, ``"v3.1"``, ``"v3.2"``, ``"v3.3"``, ``"v3.4"``: NEST 3 release versions.

For a list of the corresponding NEST Simulator repository tags, please see https://github.com/nest/nest-simulator/tags.


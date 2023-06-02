Running NESTML
##############

Running NESTML causes several processing steps to occur:

1. The model is parsed from file and checked (syntax, consistent physical units, and so on).
2. Code is generated from the model by one of the "code generators" selected when NESTML was invoked.
3. If necessary, the code is compiled and built by the "builder" that belongs to the selected code generator.

Currently, the following code generators are supported:

* `NEST Simulator <NEST Simulator target_>`_

  .. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/fig/nest-simulator-logo.png
     :width: 95px
     :height: 40px
     :target: #nest-simulator-target

* `Python-standalone <Python-standalone target_>`_

  .. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/fig/python-logo.png
     :width: 40px
     :height: 40px
     :target: #python-standalone-target


Running NESTML from Python
--------------------------

NESTML can be imported as a Python package, and can therefore be used from within other Python tools and scripts. After PyNESTML has been installed, the following function has to be imported:

.. code-block:: python

   from pynestml.frontend.pynestml_frontend import generate_target

Subsequently, it is possible to call PyNESTML from other Python tools and scripts via calls to ``generate_target()``, which generates, builds and installs code for the target platform. ``generate_target()`` can be called as follows:

.. code-block:: python

   generate_target(input_path, target_platform, target_path, install_path, logging_level, module_name, store_log, suffix, dev, codegen_opts)

The following default values are used, corresponding to the command line defaults. Possible values for ``logging_level`` are the same as before ("DEBUG", "INFO", "WARNING", "ERROR", "NO"). Note that only the ``input_path`` argument is mandatory:

.. list-table::
   :header-rows: 1
   :widths: 10 10 10

   * - Argument
     - Type
     - Default
   * - input_path
     - str or Sequence[str]
     - *no default*
   * - target_platform
     - str
     - "NEST"
   * - target_path
     - str
     - None
   * - install_path
     - str
     - None
   * - logging_level
     - str
     - "ERROR"
   * - module_name
     - str
     - "nestmlmodule"
   * - suffix
     - str
     - ""
   * - store_log
     - bool
     - False
   * - dev
     - bool
     - False
   * - codegen_opts
     - Optional[Mapping[str, Any]]
     - (Optional) A JSON equivalent Python dictionary containing additional options for the target platform code generator. A list of available options can be found under the section "Code generation options" for your intended target platform on the page :ref:`Running NESTML`.


For a detailed description of all the arguments of ``generate_target()``, see :func:`pynestml.frontend.pynestml_frontend.generate_target`.

A typical script for the NEST Simulator target could look like the following. First, import the function:

.. code-block:: python

   from pynestml.frontend.pynestml_frontend import generate_target

   generate_target(input_path="/home/nest/work/pynestml/models",
                   target_platform="NEST",
                   target_path="/tmp/nestml_target")

We can also use a shorthand function for each supported target platform (here, NEST):

.. code-block:: python

   from pynestml.frontend.pynestml_frontend import generate_nest_target

   generate_nest_target(input_path="/home/nest/work/pynestml/models",
                        target_path="/tmp/nestml_target")

To dynamically load a module with ``module_name`` equal to ``nestmlmodule`` (the default) in PyNEST can be done as follows:

.. code-block:: python

   nest.Install("nestmlmodule")

The NESTML models are then available for instantiation, for example as:

.. code-block:: python

   pre, post = nest.Create("neuron_nestml", 2)
   nest.Connect(pre, post, "one_to_one", syn_spec={"synapse_model": "synapse_nestml"})


Running NESTML from the command line
------------------------------------

The toolchain can also be executed from the command line by running:

.. code-block:: bash

   nestml ARGUMENTS

This will generate, compile, build, and install the code for a set of specified NESTML models. The following arguments can be given, corresponding to the arguments in the command line invocation:

.. list-table::
   :header-rows: 1
   :widths: 10 30

   * - Command
     - Description
   * - ``-h`` or ``--help``
     - Print help message.
   * - ``--input_path``
     - One or more input path(s). Each path is a NESTML file, or a directory containing NESTML files. Directories will be searched recursively for files matching "\*.nestml".
   * - ``--target_path``
     - (Optional) Path to target directory where generated code will be written into. Default is ``target``, which will be created in the current working directory if it does not yet exist.
   * - ``--target_platform``
     - (Optional) The name of the target platform to generate code for. Default is ``NEST``.
   * - ``--logging_level``
     - (Optional) Sets the logging level, i.e., which level of messages should be printed. Default is ERROR, available are [DEBUG, INFO, WARNING, ERROR, NO]
   * - ``--module_name``
     - (Optional) Sets the name of the module which shall be generated. Default is the name of the directory containing the models. The name has to end in "module". Default is `nestmlmodule`.
   * - ``--store_log``
     - (Optional) Stores a log.txt containing all messages in JSON notation. Default is OFF.
   * - ``--suffix``
     - (Optional) A suffix string that will be appended to the name of all generated models.
   * - ``--install_path``
     - (Optional) Path to the directory where the generated code will be installed.
   * - ``--dev``
     - (Optional) Enable development mode: code generation is attempted even for models that contain errors, and extra information is rendered in the generated code. Default is OFF.
   * - ``--codegen_opts``
     - (Optional) Path to a JSON file containing additional options for the target platform code generator. A list of available options can be found under the section "Code generation options" for your intended target platform on the page :ref:`Running NESTML`.


NEST Simulator target
---------------------

*NESTML features supported:* :doc:`neurons </nestml_language/neurons_in_nestml>`, :doc:`synapses </nestml_language/synapses_in_nestml>`, :ref:`vectors <Vectors>`, :ref:`delay differential equations <Delay Differential Equations>`, :ref:`guards <Guards>`

After NESTML completes, the NEST extension module (by default called ``"nestmlmodule"``) can either be statically linked into NEST (see `Writing an extension module <https://nest-extension-module.readthedocs.io/>`_), or loaded dynamically using the ``Install`` API call in Python.

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


Multiple input ports in NEST
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See :ref:`Multiple input ports` to specify multiple input ports in a neuron.

After generating and building the model code, a ``receptor_type`` entry is available in the status dictionary, which maps port names to numeric port indices in NEST. The receptor type can then be selected in NEST during `connection setup <https://nest-simulator.readthedocs.io/en/latest/synapses/connection_management.html#receptor-types>`_:

.. code-block:: python

   neuron = nest.Create("iaf_psc_exp_multisynapse_neuron_nestml")

   sg = nest.Create("spike_generator", params={"spike_times": [20., 80.]})
   nest.Connect(sg, neuron, syn_spec={"receptor_type" : 1, "weight": 1000.})

   sg2 = nest.Create("spike_generator", params={"spike_times": [40., 60.]})
   nest.Connect(sg2, neuron, syn_spec={"receptor_type" : 2, "weight": 1000.})

   sg3 = nest.Create("spike_generator", params={"spike_times": [30., 70.]})
   nest.Connect(sg3, neuron, syn_spec={"receptor_type" : 3, "weight": 500.})

Note that in multisynapse neurons, receptor ports are numbered starting from 1.

We furthermore wish to record the synaptic currents ``I_kernel1``, ``I_kernel2`` and ``I_kernel3``. During code generation, one buffer is created for each combination of (kernel, spike input port) that appears in convolution statements. These buffers are named by joining together the name of the kernel with the name of the spike buffer using (by default) the string "__X__". The variables to be recorded are thus named as follows:

.. code-block:: python

   mm = nest.Create('multimeter', params={'record_from': ['I_kernel1__X__spikes1',
                                                          'I_kernel2__X__spikes2',
                                                          'I_kernel3__X__spikes3'],
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

Python-standalone target
------------------------

*NESTML features supported:* :doc:`neurons </nestml_language/neurons_in_nestml>`

The aim of the Python-standalone target is to facilitate model development and debugging. The generated Python code is intended to be easy to read and understand, rather than to be fast. When satisfied with the Python target results, high-performance code can then be generated by simply switching to a different target platform.

A Python class is generated for each neuron, as well as a very simple simulator that applies some spikes to the model(s) and measures the results. This generated code can be run independently of any installed simulator (only a few common Python packages are required, like scipy for numerical integration). The following files are generated in the target directory:

.. list-table::
   :header-rows: 1
   :widths: 10 30

   * - File
     - Description
   * - ``<neuron_name>.py``
     - Generated code for the neuron model.
   * - ``neuron.py``
     - Abstract base class for neurons.
   * - ``simulator.py``
     - A very simple simulator that can be used to instantiate neurons and spike generators, make connections between them, and perform time stepping of the network.
   * - ``spike_generator.py``
     - Can be used to emit spikes at predefined points in time.
   * - ``test_python_standalone_module.py``
     - Runnable test file that instantiates the network, runs a simulation, and plots the results.
   * - ``utils.py``
     - Miscellaneous utility functions.

After the code has been generated, a simple test can can be run by calling:

.. code-block:: bash

   python3 test_python_standalone_module.py


Code generation options
~~~~~~~~~~~~~~~~~~~~~~~

Several code generator options are available; for an overview see :class:`pynestml.codegeneration.python_standalone_code_generator.PythonStandaloneCodeGenerator`.

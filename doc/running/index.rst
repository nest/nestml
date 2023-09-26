Running NESTML
##############

Running NESTML causes several processing steps to occur:

1. The model is parsed from file and checked (syntax, consistent physical units, and so on).
2. Code is generated from the model by one of the "code generators" selected when NESTML was invoked.
3. If necessary, the code is compiled and built by the "builder" that belongs to the selected code generator.


Supported target platforms
--------------------------

Currently, the following target platforms are supported for code generation. Click on each for further information:

.. grid:: 2

   .. grid-item-card::
      :text-align: center
      :class-title: sd-d-flex-row sd-align-minor-center

      :doc:`NEST Simulator </running/running_nest>`

      |nest_logo|

   .. grid-item-card::
      :text-align: center
      :class-title: sd-d-flex-row sd-align-minor-center

      :doc:`NEST Simulator (compartmental) </running/running_nest_compartmental>`

      |nest_logo|

.. grid:: 2

   .. grid-item-card::
      :text-align: center
      :class-title: sd-d-flex-row sd-align-minor-center

      :doc:`Python-standalone </running/running_python_standalone>`

      |python_logo|

   .. grid-item-card::
      :text-align: center
      :class-title: sd-d-flex-row sd-align-minor-center

      :doc:`SpiNNaker </running/running_spinnaker>`

      |spinnaker_logo|


.. |nest_logo| image:: https://raw.githubusercontent.com/nest/nestml/master/doc/fig/nest-simulator-logo.png
   :width: 95px
   :height: 40px
   :target: running_nest.html

.. |python_logo| image:: https://raw.githubusercontent.com/nest/nestml/master/doc/fig/python-logo.png
   :width: 40px
   :height: 40px
   :target: running_python_standalone.html

.. |spinnaker_logo| image:: https://raw.githubusercontent.com/nest/nestml/master/doc/fig/spinnaker_logo.svg
   :width: 40px
   :height: 40px
   :target: running_spinnaker.html

.. warning::

   To ensure correct and reproducible results, always inspect the generated code by hand. Run comprehensive numerical testing of the model(s).

   In case of doubt, please create a `GitHub Issue <https://github.com/nest/nestml/issues>`_ or write in on the `NEST mailing list <https://nest-simulator.readthedocs.io/en/latest/developer_space/guidelines/mailing_list_guidelines.html#mail-guidelines>`_. 


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

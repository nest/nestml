Running NESTML
##############

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
     - (Optional) A JSON equivalent Python dictionary containing additional options for the target platform code generator. These options are specific to a given target platform, see for example :ref:`Running NESTML with custom templates`.

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
     - (Optional) Path to a JSON file containing additional options for the target platform code generator.


NEST Simulator target
---------------------

After NESTML completes, the NEST extension module (by default called ``"nestmlmodule"``) can either be statically linked into NEST (see `Writing an extension module <https://nest.github.io/nest-simulator/extension_modules>`_), or loaded dynamically using the ``Install`` API call in Python.

Manually building the extension module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes it can be convenient to directly edit the generated code. To manually build and install the NEST extension module, go into the target directory and run:

.. code-block:: bash

   cmake -Dwith-nest=<nest_install_dir>/bin/nest-config .
   make all
   make install

where ``<nest_install_dir>`` is the installation directory of NEST (e.g. ``/home/nest/work/nest-install``).


Running NESTML with custom templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

NESTML generates model-specific code using a set of Jinja templates. For NEST, NESTML by default uses the templates in the directory `pynestml/codegeneration/resources_nest/point_neuron <https://github.com/nest/nestml/tree/master/pynestml/codegeneration/resources_nest/point_neuron>`__. (For more information on code generation using templates, see :ref:`Section 3.1: AST Transformations and Code Generation`.)

The default directory can be changed through ``--codegen_opts`` by providing a path to the custom templates as an option in a JSON file. (Note that this parameter also exists in the ``generate_target()`` function.)

.. code-block:: bash

   nestml --input_path models/neurons/iaf_psc_exp.nestml --codegen_opts /home/nest/work/codegen_options.json

An example ``codegen_options.json`` file is as follows:

.. code-block:: json

   {
        "templates":
        {
            "path": "/home/nest/work/custom_templates",
            "model_templates": {
                "neuron": ["@NEURON_NAME@.cpp.jinja2", "@NEURON_NAME@.h.jinja2"],
                "synapse": ["@SYNAPSE_NAME@.h.jinja2"]
            },
            "module_templates": ["setup/CMakeLists.txt.jinja2",
                                 "setup/@MODULE_NAME@.h.jinja2","setup/@MODULE_NAME@.cpp.jinja2"]
        }
   }

The ``templates`` option in the JSON file contains information on the custom Jinja templates to be used for code generation.
* The ``path`` option indicates the root directory of the custom Jinja templates.
* The ``model_templates`` option indicates the names of the Jinja templates for neuron and synapse model(s) or relative path to a directory containing the neuron and synapse model(s) templates.
* The ``module_templates`` option indicates the names or relative path to a directory containing the Jinja templates used to build a NEST extension module.

The escape sequence ``@NEURON_NAME@`` (resp. ``@SYNAPSE_NAME@``, ``@MODULE_NAME@``) will be replaced with the name of the neuron model (resp. synapse model or name of the module) during code generation.

The ``codegen_opts`` can also be passed to the PyNESTML function ``generate_target()`` as follows:

.. code-block:: python

   from pynestml.frontend.pynestml_frontend import generate_target

   input_path = "..."
   target_platform = "NEST"
   codegen_opts = {"templates": {"path": "/home/nest/work/custom_templates",
                                 "model_templates": {"neuron": ["@NEURON_NAME@.cpp.jinja2", "@NEURON_NAME@.h.jinja2"],
                                                     "synapse": ["@SYNAPSE_NAME@.h.jinja2"]},
                                 "module_templates": ["setup"]}}

   generate_target(input_path, target_platform, codegen_opts=codegen_opts)


Running in NEST 2.* compatibility mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To generate code that is compatible with NEST Simulator major version 2 (in particular, 2.20.\*), use the following for the code generator dictionary (this is extracted from `tests/nest_tests/nest2_compat_test.py <https://github.com/nest/nestml/blob/master/tests/nest_tests/nest2_compat_test.py>`__):

.. code-block:: python

   codegen_opts = {
       "templates": {
           "path": os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "pynestml", "codegeneration",
                                "resources_nest", "point_neuron_nest2"),
           "model_templates": ["@NEURON_NAME@.cpp.jinja2", "@NEURON_NAME@.h.jinja2"],
           "module_templates": ["setup/CMakeLists.txt.jinja2", "setup/SLI_Init.sli.jinja2",
                                "setup/@MODULE_NAME@.h.jinja2", "setup/@MODULE_NAME@.cpp.jinja2"]
   }}

The templates are in the directory `pynestml/codegeneration/resources_nest/point_neuron_nest2 <https://github.com/nest/nestml/tree/master/pynestml/codegeneration/resources_nest/point_neuron_nest2>`__.

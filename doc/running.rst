Running NESTML
##############

After the installation, the toolchain can be executed by the following command.

.. code-block:: bash

   nestml ARGUMENTS

where arguments are:

.. list-table::
   :header-rows: 1
   :widths: 10 30

   * - Command
     - Description
   * - ``-h`` or ``--help``
     - Print help message.
   * - ``--input_path``
     - One or more input path(s). Each path is a NESTML file, or a directory containing NESTML files. Directories will be searched recursively for files matching '*.nestml'.
   * - ``--target_path``
     - (Optional) Path to target directory where generated code will be written into. Default is ``target``, which will be created in the current working directory if it does not yet exist.
   * - ``--target``
     - (Optional) The name of the target platform to generate code for. Default is NEST.
   * - ``--logging_level``
     - (Optional) Sets the logging level, i.e., which level of messages should be printed. Default is ERROR, available are [INFO, WARNING, ERROR, NO]
   * - ``--module_name``
     - (Optional) Sets the name of the module which shall be generated. Default is the name of the directory containing the models. The name has to end in "module". Default is `nestmlmodule`.
   * - ``--store_log``
     - (Optional) Stores a log.txt containing all messages in JSON notation. Default is OFF.
   * - ``--suffix``
     - (Optional) A suffix string that will be appended to the name of all generated models.
   * - ``--dev``
     - (Optional) Enable development mode: code generation is attempted even for models that contain errors, and extra information is rendered in the generated code. Default is OFF.
   * - ``--codegen_opts``
     - (Optional) Path to a JSON file containing additional options for the target platform code generator.

Generated artifacts are copied to the selected target directory (default is ``target``). In order to install the models into NEST, the following commands have to be executed from within the target directory:

.. code-block:: bash

   cmake -Dwith-nest=<nest_install_dir>/bin/nest-config .
   make all
   make install

where ``<nest_install_dir>`` is the installation directory of NEST (e.g. ``/home/nest/work/nest-install``). Subsequently, the module can either be linked into NEST (see `Writing an extension module <https://nest.github.io/nest-simulator/extension_modules>`_), or loaded dynamically using the ``Install`` API call. For example, to dynamically load a module with ``module_name`` equal to ``nestmlmodule`` in PyNEST:

.. code-block:: python

   nest.Install("nestmlmodule")

PyNESTML is also available as a component and can therefore be used from within other Python tools and scripts. After PyNESTML has been installed, the following modules have to be imported:

.. code-block:: python

   from pynestml.frontend.pynestml_frontend import to_nest, install_nest

Subsequently, it is possible to call PyNESTML from other Python tools and scripts via:

.. code-block:: python

   to_nest(input_path, target_path, logging_level, module_name, store_log, dev)

This operation expects the same set of arguments as in the case of command line invocation. The following default values are used, corresponding to the command line defaults. Possible values for ``logging_level`` are the same as before ('INFO', 'WARNING', 'ERROR', 'NO'). Note that only the ``input_path`` argument is mandatory:

.. list-table::
   :header-rows: 1
   :widths: 10 10 10

   * - Argument
     - Type
     - Default
   * - input_path
     - str or Sequence[str]
     - *no default*
   * - target_path
     - string
     - None
   * - logging_level
     - string
     - 'ERROR'
   * - module_name
     - string
     - ``nestmlmodule``
   * - store_log
     - boolean
     - False
   * - dev
     - boolean
     - False
   * - codegen_opts
     - Optional[Mapping[str, Any]]
     - (Optional) A JSON equivalent Python dictionary containing additional options for the target platform code generator.

If no errors occur, the output will be generated into the specified target directory. In order to avoid an execution of all required module-installation routines by hand, PyNESTML features a function for an installation of NEST models directly into NEST:

.. code-block:: python

   install_nest(target_path, nest_path)

Here, ``target_path`` should be set to the ``target`` directory of ``to_nest()``, and ``nest_path`` points to the directory where NEST is installed (e.g., ``/home/nest/work/nest-install``). This path can conveniently be obtained from the ``nest`` module as follows:

.. code-block:: python

   import nest
   nest_path = nest.ll_api.sli_func("statusdict/prefix ::")

A typical script, therefore, could look like the following. For this example, we assume that the name of the generated module is ``nestmlmodule``.

.. code-block:: python

   from pynestml.frontend.pynestml_frontend import to_nest, install_nest

   to_nest(input_path="/home/nest/work/pynestml/models", target_path="/home/nest/work/pynestml/target")

   install_nest("/home/nest/work/pynestml/target", "/home/nest/work/nest-install")

   nest.Install("nestmlmodule")
   # ...
   nest.Simulate(400.)

Running NESTML with custom templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
NESTML generates model-specific C++ code for the NEST simulator using a set of Jinja templates. By default, NESTML uses the templates in the directory ``pynestml/codegeneration/resources_nest/point_neuron``. For more information on code generation using templates, see :ref:`Section 3.1: AST Transformations and Code Generation`.

The default directory can be changed through ``--codegen_opts`` by providing a path to the custom templates as an option in a JSON file.

.. code-block:: bash
   nestml --input_path models/iaf_psc_exp.nestml --codegen_opts /home/nest/work/codegen_options.json

An example ``codegen_options.json`` file is as follows:

.. code-block:: json
   {
        "templates":
        {
            "path": "/home/nest/work/custom_templates",
            "model_templates": {
                "neuron": ["NeuronClass.cpp.jinja2", "NeuronHeader.h.jinja2"],
                "synapse": ["SynapseHeader.h.jinja2"]
            },
            "module_templates": ["setup/CMakeLists.txt.jinja2",
                                 "setup/ModuleHeader.h.jinja2","setup/ModuleClass.cpp.jinja2"]
        }
   }

The ``templates`` option in the JSON file contains information on the custom jinja templates to be used for code generation.
* The ``path`` option indicates the root directory of the custom jinja templates.
* The ``model_templates`` option indicates a list of the jinja templates or a relative path to a directory containing the neuron and synapse model templates.
The neuron model templates are provided using the ``neuron`` sub-option and synapse templates using the ``synapse`` sub-option.
* The ``module_templates`` option indicates the names or relative path to a directory containing the jinja templates used to build a NEST extension module.

The ``codegen_opts`` can also be passed to the PyNESTML function ``to_nest`` as follows:

.. code-block:: python
   from pynestml.frontend.pynestml_frontend import to_nest
   options = {
        "templates":
        {
            "path": "/home/nest/work/custom_templates",
            "model_templates": {
                "neuron": ['NeuronClass.cpp.jinja2', 'NeuronHeader.h.jinja2'],
                "synapse": ['SynapseHeader.h.jinja2']
            },
            "module_templates": ["setup"]
        }
   }
   to_nest(input_path, target_path, logging_level, module_name, store_log, dev, options)

Running in NEST 2.* compatibility mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To generate code that is compatible with NEST Simulator major version 2 (in particular, 2.20.1), use the following for the code generator dictionary (this is extracted from `tests/nest_tests/nest2_compat_test.py <https://github.com/nest/nestml/blob/master/tests/nest_tests/nest2_compat_test.py>`__):

.. code-block:: python

   codegen_opts = {
       "neuron_parent_class_include": "archiving_node.h",
       "neuron_parent_class": "Archiving_Node",
       "templates": {
           "path": os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'pynestml', 'codegeneration',
                                'resources_nest', 'point_neuron_nest2'),
           "model_templates": {
                    "neuron": ['NeuronClass.cpp.jinja2', 'NeuronHeader.h.jinja2'],
                    "synapse":  ['SynapseHeader.h.jinja2']
           },
           "module_templates": ['setup/CMakeLists.txt.jinja2', 'setup/SLI_Init.sli.jinja2',
                                'setup/ModuleHeader.h.jinja2', 'setup/ModuleClass.cpp.jinja2']
   }}

The templates are in the directory `pynestml/codegeneration/resources_nest/point_neuron_nest2 <https://github.com/nest/nestml/tree/master/pynestml/codegeneration/resources_nest/point_neuron_nest2>`__.

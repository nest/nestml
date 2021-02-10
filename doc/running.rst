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

   install_nest(models_path, nest_path)

Here, ``models_path`` should be set to the ``target`` directory of ``to_nest()``, and ``nest_path`` points to the directory where NEST is installed (e.g., ``/home/nest/work/nest-install``). This path can conveniently be obtained from the ``nest`` module as follows:

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

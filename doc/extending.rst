Extending NESTML
################

The NESTML toolchain is lightweight, modular and extensible.


Internal workflow
-----------------

When NESTML is invoked, several steps are executed in sequence. First, the model(s) are parsed and validated. Then, depending on which target platform has been selected, transformations may occur, such as variable name rewriting in case of conflict with a keyword in the target language). The transformed models are then passed to the code generator, which combines them with a set of templates. Finally, an optional build stage compiles and builds the code, for example to yield a dynamically loadable library (``.so`` or ``.dll`` file).

.. figure:: https://raw.githubusercontent.com/nest/nestml/main/doc/fig/internal_workflow.png
   :alt: NESTML model(s) → Parsing and validation → Transform → (+ Templates) → Generate code (and build) → Executable (binary) code

A more detailed description of the internal architecture of NESTML can be found in the following places:

* Tammo Ippen, "NESTML - Creating a Neuron Modeling Language and Generating Efficient Code for the NEST Simulator with MontiCore". Master's thesis, RWTH Aachen University (2013) :download:`PDF <extending/Tammo_Ippen_Master_Thesis.pdf>`
* Konstantin Perun, "Reengineering of NestML with Python". Master's thesis, RWTH Aachen University (2018) :download:`PDF <extending/Konstantin_Perun_Master_thesis.pdf>`
* Dimitri Plotnikov, "NESTML - die Domänenspezifische Sprache für den NEST-Simulator Neuronaler Netzwerke im Human Brain Project". Doctoral thesis, RWTH Aachen University (2017) :download:`PDF <extending/Dimitri_Plotnikov_Doctoral_Thesis.pdf>`

  * A condensed online English version is available: :doc:`pynestml_toolchain/index`


Transformers
~~~~~~~~~~~~

After the models have been parsed and validated, and before code is generated, a sequence of *transformers* is applied to them. Each transformer performs a single transformation step on a set of models, for instance, renaming variables that conflict with keywords in the target language, or analysing the differential equations using ODE-toolbox. Besides modifying the models, a transformer can store information about each model in a metadata dictionary, which is available to subsequent transformers and to the code generator. For instance, the ``ODEToolboxTransformer`` stores the solvers computed by ODE-toolbox in this way.

Which transformers are applied, and in which sequence, depends on the target platform. The sequence is defined in the function ``transformers_from_target_name()`` in `pynestml_frontend.py <https://github.com/nest/nestml/blob/main/pynestml/frontend/pynestml_frontend.py>`__. The following transformers are available, listed in the order in which they are applied:

.. list-table::
   :header-rows: 1
   :widths: 30 45 25

   * - Transformer
     - Description
     - Applied for target platforms
   * - :class:`~pynestml.transformers.illegal_variable_name_transformer.IllegalVariableNameTransformer`
     - Renames variables whose names are keywords in the target language (C++ or Python).
     - NEST, SpiNNaker, GeNN (C++ keywords); Python-standalone (Python keywords)
   * - :class:`~pynestml.transformers.inline_expression_expansion_transformer.InlineExpressionExpansionTransformer`
     - Makes inline expressions self-contained, and substitutes them into the ODEs that refer to them.
     - NEST, SpiNNaker, GeNN; Python-standalone
   * - :class:`~pynestml.transformers.synapse_post_neuron_transformer.SynapsePostNeuronTransformer`
     - For neuron/synapse pairs, moves the synaptic variables that only depend on postsynaptic events into the postsynaptic neuron.
     - NEST
   * - :class:`~pynestml.transformers.convolutions_to_buffers_transformer.ConvolutionsToBuffersTransformer`
     - Replaces convolutions of kernels with spiking input ports by state variables.
     - NEST, SpiNNaker, GeNN; Python-standalone
   * - :class:`~pynestml.transformers.ode_toolbox_transformer.ODEToolboxTransformer`
     - Analyses the differential equations with `ODE-toolbox <https://ode-toolbox.readthedocs.io/>`_, and stores the analytic and/or numeric solvers in the metadata.
     - NEST, SpiNNaker, GeNN; Python-standalone

Some transformers have options, which can be passed in the same way as the code generator options; see the documentation of each transformer for details.

To add a new transformer, create a subclass of :class:`pynestml.transformers.transformer.Transformer` that implements the ``transform()`` method, and add it to the sequence in ``transformers_from_target_name()``.


API documentation
-----------------

API documentation is automatically generated from source code and can be browsed here: :mod:`pynestml` **module index**


Running NESTML with custom templates
------------------------------------

NESTML generates model-specific code using a set of Jinja templates. The templates for each target platform are located in the `pynestml/codegeneration/resources_* <https://github.com/nest/nestml/tree/main/pynestml/codegeneration>`__ subdirectories. (For more information on code generation using templates, see :ref:`Section 3.1: AST Transformations and Code Generation`.) For example, for NEST, NESTML by default uses the templates in the directory `pynestml/codegeneration/resources_nest/point_neuron <https://github.com/nest/nestml/tree/main/pynestml/codegeneration/resources_nest/point_neuron>`__. These defaults are specified in the code generator within its default values dictionary (``_default_options``, see for instance https://github.com/nest/nestml/blob/main/pynestml/codegeneration/nest_code_generator.py).

The default directory can be changed by specifying code generator options that override the default values. This can be done either by passing these options via the ``codegen_opts`` parameter of the NESTML Python API call to ``generate_target()``, or on the command line, through the ``--codegen_opts`` parameter to a JSON file. For example:

.. code-block:: bash

   nestml --input_path models/neurons/iaf_psc_exp_neuron.nestml --codegen_opts /home/nest/work/codegen_options.json

An example ``codegen_options.json`` file for NEST could look as follows:

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
* The ``module_templates`` option indicates the names or relative path to a directory containing the Jinja templates for the module.

The escape sequence ``@NEURON_NAME@`` (resp. ``@SYNAPSE_NAME@``, ``@MODULE_NAME@``) will be replaced with the name of the neuron model (resp. synapse model or name of the module) during code generation.

If a directory is given, the directory is recursively searched for templates (files ending in the ``.jinja2`` extension), for example:

.. code-block:: python

   codegen_opts = {"templates": {"module_templates": ["setup"]}}


Adding a new target platform
----------------------------

* Add a new set of templates in a new directory under `pynestml/codegeneration/resources_* <https://github.com/nest/nestml/tree/main/pynestml/codegeneration>`__.
* Implement a new code generator, for example based on the existing `nest_code_generator.py <https://github.com/nest/nestml/tree/main/pynestml/codegeneration/nest_code_generator.py>`_.
* Optionally, implement a new builder, for example based on the existing `nest_builder.py <https://github.com/nest/nestml/tree/main/pynestml/codegeneration/nest_builder.py>`_.
* Add the new target platform to the frontend in `pynestml_frontend.py <https://github.com/nest/nestml/blob/main/pynestml/frontend/pynestml_frontend.py>`__.

Welcome to the NESTML documentation
===================================

NESTML is a domain-specific language that supports the specification of neuron models in a precise and concise syntax. It was developed to address the maintainability issues that follow from an increasing number of models, model variants, and an increased model complexity in computational neuroscience. Our aim is to ease the modelling process for neuroscientists both with and without prior training in computer science. This is achieved without compromising on performance by automatic source-code generation, allowing the same model file to target different hardware or software platforms by changing  only a command-line parameter. While originally developed in the context of `NEST Simulator <https://nest-simulator.readthedocs.io/>`_, the language itself as well as the associated toolchain are lightweight, modular and extensible, by virtue of using a parser generator and internal abstract syntax tree (AST) representation, which can be operated on using well-known patterns such as visitors and rewriting. Model equations can either be given as a simple string of mathematical notation or as an algorithm written in the built-in procedural language. The equations are analyzed by the associated toolchain `ODE-toolbox <https://ode-toolbox.readthedocs.io/>`_, to compute an exact solution if possible or to invoke an appropriate numeric solver otherwise.

.. toctree::
   :glob:
   :hidden:
   :maxdepth: 1

   nestml_language
   installation
   running
   models_library/index
   pynestml_toolchain/index
   getting_help
   citing
   license


.. .. figure:: nestml-logo/nestml-logo.png
      :scale: 30 %
      :align: center

Model development with NESTML
=============================

Summary of language features and syntax
#######################################

:doc:`The NESTML language <nestml_language>`


Models library
##############

Out of the box, use any of :doc:`over 20 models <models_library/index>` that come packaged with NESTML, from standard integrate-and-fire varieties to a family of biophysical, Hodgkin-Huxley type neurons.


Tutorials
#########

* :doc:`Izhikevich tutorial <tutorial/izhikevich_tutorial>`

  Learn how to finish a partial Izhikevich spiking neuron model.


NESTML language and toolchain development
=========================================

:doc:`PyNESTML <pynestml_toolchain/index>` is the Python-based toolchain for the NESTML language: it parses the model, invokes ODE-toolbox and performs code generation. Modify PyNESTML to add language elements such as new predefined functions, or to add new target platforms.

API documentation is automatically generated from source code: :mod:`pynestml` **module index**

Internally, the `ODE-toolbox <https://ode-toolbox.readthedocs.io/>`__ Python package is used for the processing of differential equations.


.. include:: getting_help.rst


Acknowledgements
================

This software was initially supported by the JARA-HPC Seed Fund *NESTML - A modeling language for spiking neuron and synapse models for NEST* and the Initiative and Networking Fund of the Helmholtz Association and the Helmholtz Portfolio Theme *Simulation and Modeling for the Human Brain*.

This software was developed in part or in whole in the Human Brain Project, funded from the European Union's Horizon 2020 Framework Programme for Research and Innovation under Specific Grant Agreements No. 720270, No. 785907 and No. 945539 (Human Brain Project SGA1, SGA2 and SGA3).

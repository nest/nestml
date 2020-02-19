Welcome to the NESTML documentation
===================================

NESTML is a domain-specific language that supports the specification of neuron models in a precise and concise syntax, based on the syntax of Python. Model equations can either be given as a simple string of mathematical notation or as an algorithm written in the built-in procedural language. The equations are analyzed by the associated toolchain, written in Python, to compute an exact solution if possible or use an appropriate numeric solver otherwise.

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


.. figure:: nestml-logo/nestml-logo.png
   :scale: 30 %
   :align: center

Model development with NESTML
=============================

Summary of language features and syntax
#######################################

:doc:`The NESTML language <nestml_language>`


:doc:`Models library <models_library/index>`
############################################

Out of the box, use any of over 20 models that come packaged with NESTML, from standard integrate-and-fire varieties to a family of biophysical, Hodgkin-Huxley type neurons.


Tutorials
#########

* :doc:`Izhikevich tutorial <tutorial/izhikevich_tutorial>`

  Learn how to finish a partial Izhikevich spiking neuron model.


NESTML language and toolchain development
=========================================

:doc:`PyNESTML <pynestml_toolchain/index>` is the Python-based toolchain for the NESTML language: it parses the model, invokes ode-toolbox and performs code generation. Modify PyNESTML to add language elements such as new predefined functions, or to add new target platforms.


API documentation is automatically generated from source code: :mod:`pynestml` module index



.. include:: getting_help.rst

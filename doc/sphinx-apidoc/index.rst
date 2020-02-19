Welcome to the NESTML documentation
===================================

Welcome to the documentation for NESTML and PyNESTML. 

NESTML is a domain-specific language that supports the specification of neuron models in a precise and concise syntax, based on the syntax of Python. Model equations can either be given as a simple string of mathematical notation or as an algorithm written in the built-in procedural language. The equations are analyzed by the associated toolchain, written in Python, to compute an exact solution if possible or use an appropriate numeric solver otherwise.

.. toctree::
   :glob:
   :hidden:
   :maxdepth: 1

   nestml_language
   installation
   running_nestml
   models_library/index
   pynestml_toolchain/index
   getting_help
   citing
   license


.. figure:: nestml-logo/nestml-logo.png
   :scale: 30 %
   :align: center


:doc:`The NESTML language <nestml_language>`
============================================

Summary of language features and syntax.


:doc:`Models library <models_library/index>`
============================================

NESTML comes packaged with over 20 models, from standard integrate-and-fire 


Tutorials
=========

:doc:`Izhikevich tutorial <tutorial/izhikevich_tutorial>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Learn how to finish a partial Izhikevich spiking neuron model.


:doc:`The PyNESTML toolchain <pynestml_toolchain/index>`
========================================================

PyNESTML is the Python-based toolchain for the NESTML language: it parses the model, invokes ode-toolbox and performs code generation.


API documentation: :mod:`pynestml` module index
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This documentation is automatically generated from the toolchain source code in `pynestml`.


.. include installation.rst

.. include getting_help.rst

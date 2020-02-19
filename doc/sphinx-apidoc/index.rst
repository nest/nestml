Welcome to the NESTML documentation
===================================

Welcome to the documentation for NESTML and PyNESTML. 

NESTML is a domain-specific language that supports the specification of neuron models in a precise and concise syntax, based on the syntax of Python. Model equations can either be given as a simple string of mathematical notation or as an algorithm written in the built-in procedural language. The equations are analyzed by the associated toolchain, written in Python, to compute an exact solution if possible or use an appropriate numeric solver otherwise.

.. toctree::
   :glob:
   :hidden:
   :maxdepth: 1

   nestml_language
   models_library
   pynestml_toolchain/index


.. figure:: nestml-logo/nestml-logo.png
   :scale: 30 %
   :align: center


:doc:`Foobar <models_library>`

:doc:`Foobob <models_library/index>`

:doc:`Foozzy <models_library/index.rst>`


The NESTML language
===================

 * :doc:`The NESTML language <nestml_language>`

   Summary of language features and syntax.

 * :doc:`Izhikevich tutorial <tutorial/izhikevich_tutorial.rst>`

   Learn how to finish a partial Izhikevich spiking neuron model.




The PyNESTML toolchain
======================

PyNESTML is the Python-based toolchain for the NESTML language: it parses the model and invokes ode-toolbox to perform symbolic analysis of dynamics and solver selection, results which are used during code generation.

 * :doc:`Design documentation <pynestml_toolchain/index>`

   Detailed description of the design and operation of PyNESTML, the NESTML language toolchain.

 * API documentation: :mod:`pynestml` module index

   This documentation is automatically generated from the toolchain source code in `pynestml`.


Resources
=========

 * The official NESTML GitHub repository: `<https://github.com/nest/nestml>`_.

 * Installation, running PyNESTML: see the :doc:`readme`.

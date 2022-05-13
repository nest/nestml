The NESTML modeling language
============================

.. figure:: https://raw.githubusercontent.com/clinssen/nestml/doc_blurb/doc/fig/nestml_clip_art.png
   :width: 296px
   :height: 350px
   :align: right

NESTML is a domain-specific language for neuron and synapse models. These dynamical models can be used in simulations of brain activity on several platforms, in particular the `NEST Simulator <https://nest-simulator.readthedocs.org/>`_.

NESTML combines:

- an easy to understand, yet powerful syntax;
- a flexible processing toolchain, written in Python;
- good simulation performance by means of code generation (C++ for NEST Simulator).

To see what NESTML looks like, please see the :doc:`models library <models_library/index>`. The library contains a variety of models from standard integrate-and-fire to a family of biophysical, Hodgkin-Huxley type neurons, as well as several synaptic plasticity models such as spike-timing dependent plasticity (STDP) variants and third-factor plasticity rules.

:doc:`PyNESTML <pynestml_toolchain/index>` is the Python-based toolchain for the NESTML language: it parses the model and performs code generation. Modify PyNESTML to add language elements such as new predefined functions, or to add new target platforms in the form of `Jinja <https://jinja.palletsprojects.com>`_ templates.

Internally, differential equations are analyzed by the associated `ODE-toolbox <https://ode-toolbox.readthedocs.io/>`_, to compute an exact solution if possible or to select an appropriate numeric solver otherwise.


.. toctree::
   :glob:
   :hidden:
   :maxdepth: 1

   nestml_language/index
   installation
   running
   models_library/index
   tutorials/index
   pynestml_toolchain/index
   getting_help
   citing
   license

.. .. figure:: nestml-logo/nestml-logo.png
      :scale: 30 %
      :align: center


Tutorials
#########

.. include:: tutorials/tutorials_list.rst


.. include:: getting_help.rst


Acknowledgements
================

This software was initially supported by the JARA-HPC Seed Fund *NESTML - A modeling language for spiking neuron and synapse models for NEST* and the Initiative and Networking Fund of the Helmholtz Association and the Helmholtz Portfolio Theme *Simulation and Modeling for the Human Brain*.

This software was developed in part or in whole in the Human Brain Project, funded from the European Union's Horizon 2020 Framework Programme for Research and Innovation under Specific Grant Agreements No. 720270, No. 785907 and No. 945539 (Human Brain Project SGA1, SGA2 and SGA3).

Neuron and synapse illustration: copyright Sebastian B.C. Lehmann <se.lehmann@fz-juelich.de>, INM-6, Forschungszentrum Jülich GmbH (CC-BY-SA)

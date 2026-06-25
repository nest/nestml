NESTML language documentation
=============================

.. toctree::
   :maxdepth: 1

   nestml_language_concepts
   neurons_in_nestml
   synapses_in_nestml

NESTML is a domain-specific language for the specification of hybrid dynamical systems: those that combine continuous-time dynamics, often expressed as ordinary differential equations (ODEs), with discrete-time dynamics, which model instantaneous events such as neuronal spikes. NESTML was originally developed as a modelling language for the individual neurons and synapses that constitute a neural network, but is a completely generic language for any hybrid dynamical system. The language is agnostic about the numerical methods used for simulating the model, such as which numerical (ODE) solver is used; this is instead determined when code is generated for the model (see the section :ref:`Running NESTML`).

NESTML has a concise syntax based on that of Python, and is indentation-based, which avoids clutter in the form of semicolons, curly braces or tags. NESTML model files are expected to have the filename extension ``.nestml``. Each file may contain one or more models. This means that there is not necessarily a direct correspondence between model and file name; however, this is often done by convention.

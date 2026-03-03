NESTML language documentation
=============================

.. toctree::
   :maxdepth: 1

   nestml_language_concepts
   neurons_in_nestml
   synapses_in_nestml

NESTML is a domain specific language for the specification of models; typically, the individual neurons and synapses that make up a neural network. NESTML is a completely generic language for hybrid dynamical systems, that is, those that exhibit continuous-time dynamics (such as described by ordinary differential equations) as well as instantaneous events. It is agnostic of the numerical methods used for simulating the model, such as which numerical (ODE) solver is used; this is determined during code generation and will typically depend on which simulation platform is used (for instance, NEST Simulator).

NESTML has a concise syntax based on that of Python, which avoids clutter in the form of semicolons, curly braces or tags as known from other programming and description languages. NESTML model files are expected to have the filename extension ``.nestml``. Each file may contain one or more models. This means that there is not necessarily a direct correspondence between model and file name; however, this is often done by convention.

NESTML language documentation
=============================

.. toctree::
   :maxdepth: 1

   nestml_language_concepts
   neurons_in_nestml
   synapses_in_nestml

NESTML is a domain specific language for the specification of models; typically, the individual neurons and synapses that make up a neural network. NESTML is a completely generic language for hybrid dynamical systems, that is, those that exhibit continuous-time dynamics (such as described by ordinary differential equations) as well as instantaneous events. It has a concise syntax based on that of Python, which avoids clutter in the form of semicolons, curly braces or tags as known from other programming and description languages. Instead, it concentrates on domain concepts that help to efficiently create neuron and synapse models.

NESTML files are expected to have the filename extension ``.nestml``. Each file may contain one or more models. This means that there is not necessarily a direct correspondence between model and file name; however, this is often done by convention.

NESTML language documentation
=============================

.. toctree::
   :maxdepth: 1

   nestml_language_concepts
   neurons_in_nestml
   synapses_in_nestml

NESTML is a domain specific language for the specification of models. NESTML is a completely generic language, but is specifically tailored for the spiking neural network simulator `NEST <http://www.nest-simulator.org>`__. It has a concise syntax based on that of Python, which avoids clutter in the form of semicolons, curly braces or tags as known from other programming and description languages. Instead, it concentrates on domain concepts that help to efficiently create neuron and synapse models.

NESTML files are expected to have the filename extension ``.nestml``. Each file may contain one or more models (neuron or synapse). This means that there is no forced direct correspondence between model and file name. Models that shall be compiled into one extension module for NEST have to reside in the same directory. The name of the directory will be used as the name of the corresponding module.

In order to give users complete freedom in implementing model dynamics, NESTML has a full procedural programming language built in. This programming language can be used to define a custom update function that is executed on each simulation timestep, and to handle events such as receiving a spike.

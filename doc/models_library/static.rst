static
######


Static synapse

Description
+++++++++++
A synapse where the synaptic strength (weight) does not evolve with simulated time, but is defined as a (constant) parameter.

 Synaptic weight


Parameters
++++++++++


  Synaptic weight.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "w", "real", "1", "Synaptic weight"    
    "d", "ms", "1ms", "Synaptic transmission delay"
Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `static <https://github.com/nest/nestml/tree/master/models/synapses/static_synapse.nestml>`_.


Characterisation
++++++++++++++++

.. include:: static_characterisation.rst


.. footer::

   Generated at 2023-03-17 14:48:41.193757
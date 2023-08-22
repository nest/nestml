static_synapse
##############


Static synapse

Description
+++++++++++
A synapse where the synaptic strength (weight) does not evolve with simulated time, but is defined as a (constant) parameter.



Parameters
++++++++++


.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "w", "real", "1", "Synaptic weight"    
    "d", "ms", "1ms", "Synaptic transmission delay"
Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `static_synapse <https://github.com/nest/nestml/tree/master/models/synapses/static_synapse.nestml>`_.


Characterisation
++++++++++++++++

.. include:: static_synapse_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.873822
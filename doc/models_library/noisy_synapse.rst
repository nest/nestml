noisy_synapse
#############


noisy_synapse - Static synapse with Gaussian noise

Description
+++++++++++

Each presynaptic spike is passed to the postsynaptic partner with a weight sampled as :math:`w + A_\text{noise} \mathcal{N}(0, 1)`.



Parameters
++++++++++


.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "w", "real", "1", "Synaptic weight"    
    "d", "ms", "1ms", "Synaptic transmission delay"    
    "A_noise", "real", "0.4", ""
Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `noisy_synapse <https://github.com/nest/nestml/tree/master/models/synapses/noisy_synapse.nestml>`_.


Characterisation
++++++++++++++++

.. include:: noisy_synapse_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.871968
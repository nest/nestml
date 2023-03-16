noisy_synapse
#############


noisy_synapse - Static synapse with Gaussian noise

Description
+++++++++++

Each presynaptic spike is passed to the postsynaptic partner with a weight sampled as :math:`w + A_\text{noise} \mathcal{N}(0, 1)`.



Parameters
++++++++++


    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "w", "real", "1", "Synaptic weight"    
    "d", "ms", "1ms", "Synaptic transmission delay"    
    "A_noise", "real", "0.4", ""
Source code
+++++++++++

.. code-block:: nestml

   synapse noisy_synapse:
       parameters:
            w real = 1 # Synaptic weight
           d ms = 1ms @nest::delay # Synaptic transmission delay
           A_noise real = 0.4
       input:
           pre_spikes real <-spike
       output: spike
       onReceive(pre_spikes): # temporary variable for the "weight" that will be transmitted
           w_ real = w + A_noise * random_normal(0,1)
           # deliver spike to postsynaptic partner
           deliver_spike(w_,d)
    




Characterisation
++++++++++++++++

.. include:: noisy_synapse_characterisation.rst


.. footer::

   Generated at 2023-03-02 18:49:47.386807
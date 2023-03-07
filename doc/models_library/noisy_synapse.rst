noisy_synapse
#############


noisy_synapse - Static synapse with Gaussian noise

Description
+++++++++++

Each presynaptic spike is passed to the postsynaptic partner with a weight sampled as :math:`w + A_\text{noise} \mathcal{N}(0, 1)`.



Parameters
++++++++++


  !!! cannot have a variable called "delay".. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "the_delay", "ms", "1ms", "!!! cannot have a variable called ""delay"""    
    "A_noise", "real", "0.4", ""


State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "w", "nS", "1nS", ""
Source code
+++++++++++

.. code-block:: nestml

   synapse noisy_synapse:
       state:
           w nS = 1nS
       parameters: # !!! cannot have a variable called "delay"
           the_delay ms = 1ms @nest::delay # !!! cannot have a variable called "delay"
           A_noise real = 0.4
       input:
           pre_spikes nS <-spike
       output: spike
       onReceive(pre_spikes): # temporary variable for the "weight" that will be transmitted
           w_ nS = w + A_noise * random_normal(0,1)
           # deliver spike to postsynaptic partner
           deliver_spike(w_,the_delay)
    




Characterisation
++++++++++++++++

.. include:: noisy_synapse_characterisation.rst


.. footer::

   Generated at 2023-03-09 09:14:34.931768
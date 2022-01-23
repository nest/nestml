noisy_synapse
#############





Parameters
++++++++++



.. csv-table::
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
     end
     parameters:
       the_delay ms = 1ms # !!! cannot have a variable called "delay"
       A_noise real = 0.4
     end
     input:
       pre_spikes nS <-spike
     end

     output: spike

     onReceive(pre_spikes):
       # temporary variable for the "weight" that will be transmitted
       w_ nS = w + A_noise * random_normal(0,1)
       # deliver spike to postsynaptic partner
       deliver_spike(w_,the_delay)
     end

   end



Characterisation
++++++++++++++++

.. include:: noisy_synapse_characterisation.rst


.. footer::

   Generated at 2021-12-09 08:22:33.025794
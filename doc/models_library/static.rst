static
######


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

.. code-block:: nestml

   synapse static:
     parameters:
       w real = 1 @nest::weight # Synaptic weight
       d ms = 1ms @nest::delay # Synaptic transmission delay
     end
     input:
       pre_spikes real <-spike
     end

     onReceive(pre_spikes):
       deliver_spike(w,d)
     end

   end



Characterisation
++++++++++++++++

.. include:: static_characterisation.rst


.. footer::

   Generated at 2023-03-02 18:49:47.383073
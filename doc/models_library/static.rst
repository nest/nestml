static
######




Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "w", "real", "900", ""    
    "d", "ms", "0.9ms", ""    
    "a", "real", "3.141592653589793", ""    
    "b", "real", "100.0", ""

Source code
+++++++++++

.. code-block:: nestml

   synapse static:
     parameters:
       w real = 900
       d ms = 0.9ms
       a real = 3.141592653589793
       b real = 100.0
     end
     input:
       pre_spikes mV <-spike
     end

     onReceive(pre_spikes):
       deliver_spike(0.00318 * a * b * w,d)
     end

   end



Characterisation
++++++++++++++++

.. include:: static_characterisation.rst


.. footer::

   Generated at 2021-12-09 08:22:33.027750
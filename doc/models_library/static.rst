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

    
    "w", "real", "900", ""    
    "d", "ms", "0.9ms", ""    
    "a", "real", "3.141592653589793", ""    
    "b", "real", "100.0", ""
Source code
+++++++++++

.. code-block:: nestml

   synapse static:
       parameters:
           w real = 900 @nest::weight @45
           d ms = 0.9ms @nest::delay @46
           a real = 3.141592653589793 @nest::a @45
           b real = 100.0 @nest::b @46
       input:
           pre_spikes mV <-spike
       onReceive(pre_spikes):
           deliver_spike(0.00318 * a * b * w,d)
    




Characterisation
++++++++++++++++

.. include:: static_characterisation.rst


.. footer::

   Generated at 2023-03-09 09:14:34.933019
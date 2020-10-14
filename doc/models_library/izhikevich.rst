izhikevich
##########

izhikevich - Izhikevich neuron model


Description
+++++++++++

Implementation of the simple spiking neuron model introduced by Izhikevich [1]_. The dynamics are given by:

.. math::

   dv/dt &= 0.04 v^2 + 5 v + 140 - u + I\\
   du/dt &= a (b v - u)


.. math::

   &\text{if}\;\; v \geq V_{th}:\\
   &\;\;\;\; v \text{ is set to } c\\
   &\;\;\;\; u \text{ is incremented by } d\\
   & \, \\
   &v \text{ jumps on each spike arrival by the weight of the spike}

As published in [1]_, the numerics differs from the standard forward Euler technique in two ways:

1) the new value of :math:`u` is calculated based on the new value of :math:`v`, rather than the previous value
2) the variable :math:`v` is updated using a time step half the size of that used to update variable :math:`u`.

This model will instead be simulated using the numerical solver that is recommended by ODE-toolbox during code generation.


Authors
+++++++

Hanuschkin, Morrison, Kunkel


References
++++++++++

.. [1] Izhikevich, Simple Model of Spiking Neurons, IEEE Transactions on Neural Networks (2003) 14:1569-1572


Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "a", "real", "0.02", "describes time scale of recovery variable"    
    "b", "real", "0.2", "sensitivity of recovery variable"    
    "c", "mV", "-65mV", "after-spike reset value of V_m"    
    "d", "real", "8.0", "after-spike reset value of U_m"    
    "V_m_init", "mV", "-70mV", "initial membrane potential"    
    "V_min", "mV", "-inf * mV", "Absolute lower value for the membrane potential."    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "V_m_init", "Membrane potential"    
    "U_m", "real", "b * V_m_init", "Membrane potential recovery variable"




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\frac{ 0.04 \cdot V_{m} \cdot V_{m} } { \mathrm{mV} } + 5.0 \cdot V_{m} + (140 - U_{m}) \cdot \mathrm{mV} + ((I_{e} + I_{stim}) \cdot \mathrm{GOhm})) } \right) 


.. math::
   \frac{ dU_{m} } { dt }= \frac{ a \cdot (b \cdot V_{m} - U_{m} \cdot \mathrm{mV}) } { (\mathrm{mV} \cdot \mathrm{ms}) }





Source code
+++++++++++

.. code:: nestml

   neuron izhikevich:
     initial_values:
       V_m mV = V_m_init # Membrane potential
       U_m real = b * V_m_init # Membrane potential recovery variable
     end
     equations:
       V_m'=(0.04 * V_m * V_m / mV + 5.0 * V_m + (140 - U_m) * mV + ((I_e + I_stim) * GOhm)) / ms
       U_m'=a * (b * V_m - U_m * mV) / (mV * ms)
     end

     parameters:
       a real = 0.02 # describes time scale of recovery variable
       b real = 0.2 # sensitivity of recovery variable
       c mV = -65mV # after-spike reset value of V_m
       d real = 8.0 # after-spike reset value of U_m
       V_m_init mV = -70mV # initial membrane potential
       V_min mV = -inf * mV # Absolute lower value for the membrane potential.

       /* constant external input current*/
       I_e pA = 0pA
     end
     input:
       spikes mV <-spike
       I_stim pA <-current
     end

     output: spike

     update:
       integrate_odes()
       /* Add synaptic current*/

       /* Add synaptic current*/
       V_m += spikes

       /* lower bound of membrane potential*/
       V_m = (V_m < V_min)?V_min:V_m

       /* threshold crossing*/
       if V_m >= 30mV:
         V_m = c
         U_m += d
         emit_spike()
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: izhikevich_characterisation.rst


.. footer::

   Generated at 2020-05-27 18:26:44.928927
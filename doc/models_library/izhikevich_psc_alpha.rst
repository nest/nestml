izhikevich_psc_alpha
####################

izhikevich_psc_alpha - Detailed Izhikevich neuron model with alpha-kernel post-synaptic current


Description
+++++++++++

Implementation of the simple spiking neuron model introduced by Izhikevich [1]_, with membrane potential in (milli)volt
and current-based synapses.

The dynamics are given by:

.. math::

   C_m \frac{dV_m}{dt} = k (V - V_t)(V - V_t) - u + I + I_{syn,ex} + I_{syn,in}
   \frac{dU_m}{dt} = a(b(V_m - E_L) - U_m)

   &\text{if}\;\;\; V_m \geq V_{th}:\\
   &\;\;\;\; V_m \text{ is set to } c
   &\;\;\;\; U_m \text{ is incremented by } d

On each spike arrival, the membrane potential is subject to an alpha-kernel current of the form:

.. math::

  I_syn = I_0 \cdot t \cdot \exp\left(-t/\tau_{syn}\right) / \tau_{syn}

See also
++++++++

izhikevich, iaf_psc_alpha


References
++++++++++

.. [1] Izhikevich, Simple Model of Spiking Neurons, IEEE Transactions on Neural Networks (2003) 14:1569-1572


Authors
+++++++

Hanuschkin, Morrison, Kunkel


Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "C_m", "pF", "200.0pF", "Membrane capacitance"    
    "k", "pF / (ms mV)", "8.0pF / mV / ms", "Spiking slope"    
    "V_r", "mV", "-65.0mV", "resting potential"    
    "V_t", "mV", "-45.0mV", "threshold potential"    
    "a", "1 / ms", "0.01 / ms", "describes time scale of recovery variable"    
    "b", "nS", "9.0nS", "sensitivity of recovery variable"    
    "c", "mV", "-65mV", "after-spike reset value of V_m"    
    "d", "pA", "60.0pA", "after-spike reset value of U_m"    
    "V_peak", "mV", "0.0mV", "Spike detection threashold (reset condition)"    
    "tau_syn_ex", "ms", "0.2ms", "Synaptic Time Constant Excitatory Synapse"    
    "tau_syn_in", "ms", "2.0ms", "Synaptic Time Constant for Inhibitory Synapse"    
    "t_ref", "ms", "2.0ms", "Refractory period"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "-65mV", "Membrane potential"    
    "U_m", "pA", "0pA", "Membrane potential recovery variable"




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (k \cdot (V_{m} - V_{r}) \cdot (V_{m} - V_{t}) - U_{m} + I_{e} + I_{stim} + I_{syn,inh} + I_{syn,exc}) } \right) 


.. math::
   \frac{ dU_{m} } { dt }= a \cdot (b \cdot (V_{m} - V_{r}) - U_{m})





Source code
+++++++++++

.. code:: nestml

   neuron izhikevich_psc_alpha:
     state:
       r integer  # number of steps in the current refractory phase
     end
     initial_values:
       V_m mV = -65mV # Membrane potential
       U_m pA = 0pA # Membrane potential recovery variable
     end
     equations:

       /* synapses: alpha functions*/
       kernel I_syn_in = (e / tau_syn_in) * t * exp(-t / tau_syn_in)
       kernel I_syn_ex = (e / tau_syn_ex) * t * exp(-t / tau_syn_ex)
       function I_syn_exc pA = convolve(I_syn_ex,spikesExc)
       function I_syn_inh pA = convolve(I_syn_in,spikesInh)
       V_m'=(k * (V_m - V_r) * (V_m - V_t) - U_m + I_e + I_stim + I_syn_inh + I_syn_exc) / C_m
       U_m'=a * (b * (V_m - V_r) - U_m)
     end

     parameters:
       C_m pF = 200.0pF # Membrane capacitance
       k pF/mV/ms = 8.0pF / mV / ms # Spiking slope
       V_r mV = -65.0mV # resting potential
       V_t mV = -45.0mV # threshold potential
       a 1/ms = 0.01 / ms # describes time scale of recovery variable
       b nS = 9.0nS # sensitivity of recovery variable
       c mV = -65mV # after-spike reset value of V_m
       d pA = 60.0pA # after-spike reset value of U_m
       V_peak mV = 0.0mV # Spike detection threashold (reset condition)
       tau_syn_ex ms = 0.2ms # Synaptic Time Constant Excitatory Synapse
       tau_syn_in ms = 2.0ms # Synaptic Time Constant for Inhibitory Synapse
       t_ref ms = 2.0ms # Refractory period

       /* constant external input current*/
       I_e pA = 0pA
     end
     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end
     input:
       spikesInh pA <-inhibitory spike
       spikesExc pA <-excitatory spike
       I_stim pA <-current
     end

     output: spike

     update:
       integrate_odes()

       /* refractoriness and threshold crossing*/
       if r > 0: # is refractory?
         r -= 1
       elif V_m >= V_peak:
         V_m = c
         U_m += d
         emit_spike()
         r = RefractoryCounts
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: izhikevich_psc_alpha_characterisation.rst


.. footer::

   Generated at 2020-05-27 18:26:44.646052

izhikevich_psc_alpha
####################




Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "C_m", "pF", "200pF", "Membrane capacitance"    
    "k", "pF / (ms mV)", "8pF / mV / ms", "Spiking slope"    
    "V_r", "mV", "-65mV", "Resting potential"    
    "V_t", "mV", "-45mV", "Threshold potential"    
    "a", "1 / ms", "0.01 / ms", "Time scale of recovery variable"    
    "b", "nS", "9nS", "Sensitivity of recovery variable"    
    "c", "mV", "-65mV", "After-spike reset value of V_m"    
    "d", "pA", "60pA", "After-spike reset value of U_m"    
    "V_peak", "mV", "0mV", "Spike detection threshold (reset condition)"    
    "tau_syn_exc", "ms", "0.2ms", "Synaptic time constant of excitatory synapse"    
    "tau_syn_inh", "ms", "2ms", "Synaptic time constant of inhibitory synapse"    
    "t_ref", "ms", "2ms", "Refractory period"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "Number of steps in the current refractory phase"    
    "V_m", "mV", "-65mV", "Membrane potential"    
    "U_m", "pA", "0pA", "Membrane potential recovery variable"




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (k \cdot (V_{m} - V_{r}) \cdot (V_{m} - V_{t}) - U_{m} + I_{e} + I_{stim} + I_{syn,exc} - I_{syn,inh}) } \right) 


.. math::
   \frac{ dU_{m} } { dt }= a \cdot (b \cdot (V_{m} - V_{r}) - U_{m})





Source code
+++++++++++

.. code-block:: nestml

   neuron izhikevich_psc_alpha:
     state:
       r integer = 0 # Number of steps in the current refractory phase
       V_m mV = -65mV # Membrane potential
       U_m pA = 0pA # Membrane potential recovery variable
     end
     equations:
       # synapses: alpha functions
       kernel K_syn_inh = (e / tau_syn_inh) * t * exp(-t / tau_syn_inh)
       kernel K_syn_exc = (e / tau_syn_exc) * t * exp(-t / tau_syn_exc)
       inline I_syn_exc pA = convolve(K_syn_exc,exc_spikes)
       inline I_syn_inh pA = convolve(K_syn_inh,inh_spikes)
       V_m'=(k * (V_m - V_r) * (V_m - V_t) - U_m + I_e + I_stim + I_syn_exc - I_syn_inh) / C_m
       U_m'=a * (b * (V_m - V_r) - U_m)
     end

     parameters:
       C_m pF = 200pF # Membrane capacitance
       k pF/mV/ms = 8pF / mV / ms # Spiking slope
       V_r mV = -65mV # Resting potential
       V_t mV = -45mV # Threshold potential
       a 1/ms = 0.01 / ms # Time scale of recovery variable
       b nS = 9nS # Sensitivity of recovery variable
       c mV = -65mV # After-spike reset value of V_m
       d pA = 60pA # After-spike reset value of U_m
       V_peak mV = 0mV # Spike detection threshold (reset condition)
       tau_syn_exc ms = 0.2ms # Synaptic time constant of excitatory synapse
       tau_syn_inh ms = 2ms # Synaptic time constant of inhibitory synapse
       t_ref ms = 2ms # Refractory period
       # constant external input current

       # constant external input current
       I_e pA = 0pA
     end
     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end
     input:
       inh_spikes pA <-inhibitory spike
       exc_spikes pA <-excitatory spike
       I_stim pA <-current
     end

     output: spike

     update:
       integrate_odes()
       # refractoriness and threshold crossing
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

   Generated at 2022-03-28 19:04:30.156838
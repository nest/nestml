iaf_cond_exp
############


iaf_cond_exp - Simple conductance based leaky integrate-and-fire neuron model

Description
+++++++++++

iaf_cond_exp is an implementation of a spiking neuron using IAF dynamics with
conductance-based synapses. Incoming spike events induce a post-synaptic change
of conductance modelled by an exponential function. The exponential function
is normalised such that an event of weight 1.0 results in a peak conductance of
1 nS.

References
++++++++++

.. [1] Meffin H, Burkitt AN, Grayden DB (2004). An analytical
       model for the large, fluctuating synaptic conductance state typical of
       neocortical neurons in vivo. Journal of Computational Neuroscience,
       16:159-175.
       DOI: https://doi.org/10.1023/B:JCNS.0000014108.03012.81

See also
++++++++

iaf_psc_delta, iaf_psc_exp, iaf_cond_exp



Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_th", "mV", "-55mV", "Threshold potential"    
    "V_reset", "mV", "-60mV", "Reset potential"    
    "t_ref", "ms", "2ms", "Refractory period"    
    "g_L", "nS", "16.6667nS", "Leak conductance"    
    "C_m", "pF", "250pF", "Membrane capacitance"    
    "E_exc", "mV", "0mV", "Excitatory reversal potential"    
    "E_inh", "mV", "-85mV", "Inhibitory reversal potential"    
    "E_L", "mV", "-70mV", "Leak reversal potential (aka resting potential)"    
    "tau_syn_exc", "ms", "0.2ms", "Synaptic time constant of excitatory synapse"    
    "tau_syn_inh", "ms", "2ms", "Synaptic time constant of inhibitory synapse"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "counts number of tick during the refractory period"    
    "V_m", "mV", "E_L", "membrane potential"




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-I_{leak} - I_{syn,exc} - I_{syn,inh} + I_{e} + I_{stim}) } \right) 





Source code
+++++++++++

.. code-block:: nestml

   neuron iaf_cond_exp:
     state:
       r integer = 0 # counts number of tick during the refractory period
       V_m mV = E_L # membrane potential
     end
     equations:
       kernel g_inh = exp(-t / tau_syn_inh) # inputs from the inh conductance
       kernel g_exc = exp(-t / tau_syn_exc) # inputs from the exc conductance
       inline I_syn_exc pA = convolve(g_exc,exc_spikes) * (V_m - E_exc)
       inline I_syn_inh pA = convolve(g_inh,inh_spikes) * (V_m - E_inh)
       inline I_leak pA = g_L * (V_m - E_L)
       V_m'=(-I_leak - I_syn_exc - I_syn_inh + I_e + I_stim) / C_m
     end

     parameters:
       V_th mV = -55mV # Threshold potential
       V_reset mV = -60mV # Reset potential
       t_ref ms = 2ms # Refractory period
       g_L nS = 16.6667nS # Leak conductance
       C_m pF = 250pF # Membrane capacitance
       E_exc mV = 0mV # Excitatory reversal potential
       E_inh mV = -85mV # Inhibitory reversal potential
       E_L mV = -70mV # Leak reversal potential (aka resting potential)
       tau_syn_exc ms = 0.2ms # Synaptic time constant of excitatory synapse
       tau_syn_inh ms = 2ms # Synaptic time constant of inhibitory synapse
       # constant external input current

       # constant external input current
       I_e pA = 0pA
     end
     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end
     input:
       inh_spikes nS <-inhibitory spike
       exc_spikes nS <-excitatory spike
       I_stim pA <-current
     end

     output: spike

     update:
       integrate_odes()
       if r != 0: # neuron is absolute refractory
         r = r - 1
         V_m = V_reset # clamp potential
       elif V_m >= V_th:
         r = RefractoryCounts
         V_m = V_reset # clamp potential
         emit_spike()
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: iaf_cond_exp_characterisation.rst


.. footer::

   Generated at 2022-03-28 19:04:30.212547
iaf_cond_alpha
##############

iaf_cond_alpha - Simple conductance based leaky integrate-and-fire neuron model


Description
+++++++++++

iaf_cond_alpha is an implementation of a spiking neuron using IAF dynamics with
conductance-based synapses. Incoming spike events induce a post-synaptic change
of conductance modelled by an alpha function. The alpha function
is normalised such that an event of weight 1.0 results in a peak current of 1 nS
at :math:`t = \tau_{syn}`.


References
++++++++++

.. [1] Meffin H, Burkitt AN, Grayden DB (2004). An analytical
       model for the large, fluctuating synaptic conductance state typical of
       neocortical neurons in vivo. Journal of Computational Neuroscience,
       16:159-175.
       DOI: https://doi.org/10.1023/B:JCNS.0000014108.03012.81
.. [2] Bernander O, Douglas RJ, Martin KAC, Koch C (1991). Synaptic background
       activity influences spatiotemporal integration in single pyramidal
       cells.  Proceedings of the National Academy of Science USA,
       88(24):11569-11573.
       DOI: https://doi.org/10.1073/pnas.88.24.11569
.. [3] Kuhn A, Rotter S (2004) Neuronal integration of synaptic input in
       the fluctuation- driven regime. Journal of Neuroscience,
       24(10):2345-2356
       DOI: https://doi.org/10.1523/JNEUROSCI.3349-03.2004

See also
++++++++

iaf_cond_exp


Authors
+++++++

Schrader, Plesser


Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_th", "mV", "-55.0mV", "Threshold Potential"    
    "V_reset", "mV", "-60.0mV", "Reset Potential"    
    "t_ref", "ms", "2.0ms", "Refractory period"    
    "g_L", "nS", "16.6667nS", "Leak Conductance"    
    "C_m", "pF", "250.0pF", "Membrane Capacitance"    
    "E_ex", "mV", "0mV", "Excitatory reversal Potential"    
    "E_in", "mV", "-85.0mV", "Inhibitory reversal Potential"    
    "E_L", "mV", "-70.0mV", "Leak reversal Potential (aka resting potential)"    
    "tau_syn_ex", "ms", "0.2ms", "Synaptic Time Constant Excitatory Synapse"    
    "tau_syn_in", "ms", "2.0ms", "Synaptic Time Constant for Inhibitory Synapse"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "E_L", "membrane potential"




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-I_{leak} - I_{syn,exc} - I_{syn,inh} + I_{e} + I_{stim}) } \right) 





Source code
+++++++++++

.. code:: nestml

   neuron iaf_cond_alpha:
     state:
       r integer  # counts number of tick during the refractory period
     end
     initial_values:
       V_m mV = E_L # membrane potential
     end
     equations:
       kernel g_in = (e / tau_syn_in) * t * exp(-t / tau_syn_in)
       kernel g_ex = (e / tau_syn_ex) * t * exp(-t / tau_syn_ex)
       function I_syn_exc pA = convolve(g_ex,spikeExc) * (V_m - E_ex)
       function I_syn_inh pA = convolve(g_in,spikeInh) * (V_m - E_in)
       function I_leak pA = g_L * (V_m - E_L)
       V_m'=(-I_leak - I_syn_exc - I_syn_inh + I_e + I_stim) / C_m
     end

     parameters:
       V_th mV = -55.0mV # Threshold Potential
       V_reset mV = -60.0mV # Reset Potential
       t_ref ms = 2.0ms # Refractory period
       g_L nS = 16.6667nS # Leak Conductance
       C_m pF = 250.0pF # Membrane Capacitance
       E_ex mV = 0mV # Excitatory reversal Potential
       E_in mV = -85.0mV # Inhibitory reversal Potential
       E_L mV = -70.0mV # Leak reversal Potential (aka resting potential)
       tau_syn_ex ms = 0.2ms # Synaptic Time Constant Excitatory Synapse
       tau_syn_in ms = 2.0ms # Synaptic Time Constant for Inhibitory Synapse

       /* constant external input current*/
       I_e pA = 0pA
     end
     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end
     input:
       spikeInh nS <-inhibitory spike
       spikeExc nS <-excitatory spike
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

.. include:: iaf_cond_alpha_characterisation.rst


.. footer::

   Generated at 2020-05-27 18:26:44.357595
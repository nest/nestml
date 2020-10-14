iaf_cond_exp_sfa_rr
###################

iaf_cond_exp_sfa_rr - Conductance based leaky integrate-and-fire model with spike-frequency adaptation and relative refractory mechanisms


Description
+++++++++++

iaf_cond_exp_sfa_rr is an implementation of a spiking neuron using integrate-and-fire dynamics with conductance-based
synapses, with additional spike-frequency adaptation and relative refractory mechanisms as described in [2]_, page 166.

Incoming spike events induce a post-synaptic change of conductance modelled by an exponential function. The exponential
function is normalised such that an event of weight 1.0 results in a peak current of 1 nS.

Outgoing spike events induce a change of the adaptation and relative refractory conductances by q_sfa and q_rr,
respectively. Otherwise these conductances decay exponentially with time constants tau_sfa and tau_rr, respectively.


References
++++++++++

.. [1] Meffin H, Burkitt AN, Grayden DB (2004). An analytical
       model for the large, fluctuating synaptic conductance state typical of
       neocortical neurons in vivo. Journal of Computational Neuroscience,
       16:159-175.
       DOI: https://doi.org/10.1023/B:JCNS.0000014108.03012.81
.. [2] Dayan P, Abbott LF (2001). Theoretical neuroscience: Computational and
       mathematical modeling of neural systems. Cambridge, MA: MIT Press.
       https://pure.mpg.de/pubman/faces/ViewItemOverviewPage.jsp?itemId=item_3006127


See also
++++++++

aeif_cond_alpha, aeif_cond_exp, iaf_chxk_2008


Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_th", "mV", "-57.0mV", "Threshold Potential"    
    "V_reset", "mV", "-70.0mV", "Reset Potential"    
    "t_ref", "ms", "0.5ms", "Refractory period"    
    "g_L", "nS", "28.95nS", "Leak Conductance"    
    "C_m", "pF", "289.5pF", "Membrane Capacitance"    
    "E_ex", "mV", "0mV", "Excitatory reversal Potential"    
    "E_in", "mV", "-75.0mV", "Inhibitory reversal Potential"    
    "E_L", "mV", "-70.0mV", "Leak reversal Potential (aka resting potential)"    
    "tau_syn_ex", "ms", "1.5ms", "Synaptic Time Constant Excitatory Synapse"    
    "tau_syn_in", "ms", "10.0ms", "Synaptic Time Constant for Inhibitory Synapse"    
    "q_sfa", "nS", "14.48nS", "Outgoing spike activated quantal spike-frequency adaptation conductance increase"    
    "q_rr", "nS", "3214.0nS", "Outgoing spike activated quantal relative refractory conductance increase."    
    "tau_sfa", "ms", "110.0ms", "Time constant of spike-frequency adaptation."    
    "tau_rr", "ms", "1.97ms", "Time constant of the relative refractory mechanism."    
    "E_sfa", "mV", "-70.0mV", "spike-frequency adaptation conductance reversal potential"    
    "E_rr", "mV", "-70.0mV", "relative refractory mechanism conductance reversal potential"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "E_L", "membrane potential"    
    "g_sfa", "nS", "0nS", "inputs from the sfa conductance"    
    "g_rr", "nS", "0nS", "inputs from the rr conductance"




Equations
+++++++++




.. math::
   \frac{ dg_{sfa} } { dt }= \frac{ -g_{sfa} } { \tau_{sfa} }


.. math::
   \frac{ dg_{rr} } { dt }= \frac{ -g_{rr} } { \tau_{rr} }


.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-I_{L} + I_{e} + I_{stim} - I_{syn,exc} - I_{syn,inh} - I_{sfa} - I_{rr}) } \right) 





Source code
+++++++++++

.. code:: nestml

   neuron iaf_cond_exp_sfa_rr:
     state:
       r integer  # counts number of tick during the refractory period
     end
     initial_values:
       V_m mV = E_L # membrane potential
       g_sfa nS = 0nS # inputs from the sfa conductance
       g_rr nS = 0nS # inputs from the rr conductance
     end
     equations:
       kernel g_in = exp(-t / tau_syn_in) # inputs from the inh conductance
       kernel g_ex = exp(-t / tau_syn_ex) # inputs from the exc conductance
       g_sfa'=-g_sfa / tau_sfa
       g_rr'=-g_rr / tau_rr
       function I_syn_exc pA = convolve(g_ex,spikesExc) * (V_m - E_ex)
       function I_syn_inh pA = convolve(g_in,spikesInh) * (V_m - E_in)
       function I_L pA = g_L * (V_m - E_L)
       function I_sfa pA = g_sfa * (V_m - E_sfa)
       function I_rr pA = g_rr * (V_m - E_rr)
       V_m'=(-I_L + I_e + I_stim - I_syn_exc - I_syn_inh - I_sfa - I_rr) / C_m
     end

     parameters:
       V_th mV = -57.0mV # Threshold Potential
       V_reset mV = -70.0mV # Reset Potential
       t_ref ms = 0.5ms # Refractory period
       g_L nS = 28.95nS # Leak Conductance
       C_m pF = 289.5pF # Membrane Capacitance
       E_ex mV = 0mV # Excitatory reversal Potential
       E_in mV = -75.0mV # Inhibitory reversal Potential
       E_L mV = -70.0mV # Leak reversal Potential (aka resting potential)
       tau_syn_ex ms = 1.5ms # Synaptic Time Constant Excitatory Synapse
       tau_syn_in ms = 10.0ms # Synaptic Time Constant for Inhibitory Synapse
       q_sfa nS = 14.48nS # Outgoing spike activated quantal spike-frequency adaptation conductance increase
       q_rr nS = 3214.0nS # Outgoing spike activated quantal relative refractory conductance increase.
       tau_sfa ms = 110.0ms # Time constant of spike-frequency adaptation.
       tau_rr ms = 1.97ms # Time constant of the relative refractory mechanism.
       E_sfa mV = -70.0mV # spike-frequency adaptation conductance reversal potential
       E_rr mV = -70.0mV # relative refractory mechanism conductance reversal potential

       /* constant external input current*/
       I_e pA = 0pA
     end
     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end
     input:
       spikesInh nS <-inhibitory spike
       spikesExc nS <-excitatory spike
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
         g_sfa += q_sfa
         g_rr += q_rr
         emit_spike()
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: iaf_cond_exp_sfa_rr_characterisation.rst


.. footer::

   Generated at 2020-05-27 18:26:44.821174
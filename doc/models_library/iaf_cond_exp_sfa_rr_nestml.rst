iaf_cond_exp_sfa_rr_nestml
==========================

Name: iaf_cond_exp_sfa_rr - Simple conductance based leaky integrate-and-fire neuron model. Description: iaf_cond_exp_sfa_rr is an iaf_cond_exp_sfa_rr i.e. an implementation of a spiking neuron using IAF dynamics with conductance-based synapses, with additional spike-frequency adaptation and relative refractory mechanisms as described in Dayan+Abbott, 2001, page 166. As for the iaf_cond_exp_sfa_rr, Incoming spike events induce a post-synaptic change of conductance modelled by an exponential function. The exponential function is normalised such that an event of weight 1.0 results in a peak current of 1 nS. Outgoing spike events induce a change of the adaptation and relative refractory conductances by q_sfa and q_rr, respectively. Otherwise these conductances decay exponentially with time constants tau_sfa and tau_rr, respectively. Sends: SpikeEvent Receives: SpikeEvent, CurrentEvent, DataLoggingRequest References: Meffin, H., Burkitt, A. N., & Grayden, D. B. (2004). An analytical model for the large, fluctuating synaptic conductance state typical of neocortical neurons in vivo. J. Comput. Neurosci., 16, 159-175. Dayan, P. and Abbott, L. F. (2001). Theoretical Neuroscience, MIT Press (p166) Author: Sven Schrader, Eilif Muller SeeAlso: iaf_cond_exp_sfa_rr, aeif_cond_alpha, iaf_psc_delta, iaf_psc_exp, iaf_cond_alpha



Parameters
----------



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
---------------

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto    
    "V_m", "mV", "E_L", "membrane potential"    
    "g_sfa", "nS", "0nS", "inputs from the sfa conductance"    
    "g_rr", "nS", "0nS", "inputs from the rr conductance"




Equations
---------




.. math::
   \frac{ dg_{sfa}' } { dt }= \frac{ -g_{sfa} } { \tau_{sfa} }


.. math::
   \frac{ dg_{rr}' } { dt }= \frac{ -g_{rr} } { \tau_{rr} }


.. math::
   \frac{ dV_{m}' } { dt }= \frac 1 { C_{m} } \left( { (-I_{L} + I_{e} + I_{stim} - I_{syn,exc} - I_{syn,inh} - I_{sfa} - I_{rr}) } \right) 





Source code
-----------

.. code:: nestml

   """
   Name: iaf_cond_exp_sfa_rr - Simple conductance based leaky integrate-and-fire
                               neuron model.

   Description:
   iaf_cond_exp_sfa_rr is an iaf_cond_exp_sfa_rr i.e. an implementation of a
   spiking neuron using IAF dynamics with conductance-based synapses,
   with additional spike-frequency adaptation and relative refractory
   mechanisms as described in Dayan+Abbott, 2001, page 166.

   As for the iaf_cond_exp_sfa_rr, Incoming spike events induce a post-synaptic
   change  of  conductance  modelled  by an  exponential  function.  The
   exponential function is  normalised such that an event  of weight 1.0
   results in a peak current of 1 nS.

   Outgoing spike events induce a change of the adaptation and relative
   refractory conductances by q_sfa and q_rr, respectively.  Otherwise
   these conductances decay exponentially with time constants tau_sfa
   and tau_rr, respectively.

   Sends: SpikeEvent

   Receives: SpikeEvent, CurrentEvent, DataLoggingRequest


   References:

   Meffin, H., Burkitt, A. N., & Grayden, D. B. (2004). An analytical
   model for the large, fluctuating synaptic conductance state typical of
   neocortical neurons in vivo. J.  Comput. Neurosci., 16, 159-175.

   Dayan, P. and Abbott, L. F. (2001). Theoretical Neuroscience, MIT Press (p166)

   Author: Sven Schrader, Eilif Muller

   SeeAlso: iaf_cond_exp_sfa_rr, aeif_cond_alpha, iaf_psc_delta, iaf_psc_exp,
   iaf_cond_alpha
   """
   neuron iaf_cond_exp_sfa_rr:

     state:
       r integer    # counts number of tick during the refractory period
     end

     initial_values:
       V_m mV = E_L # membrane potential
       g_sfa nS = 0 nS     # inputs from the sfa conductance
       g_rr nS = 0 nS      # inputs from the rr conductance
     end

     equations:
       shape g_in = exp(-t/tau_syn_in) # inputs from the inh conductance
       shape g_ex = exp(-t/tau_syn_ex) # inputs from the exc conductance

       g_sfa' = -g_sfa / tau_sfa
       g_rr' = -g_rr / tau_rr

       function I_syn_exc pA = convolve(g_ex, spikesExc) * ( V_m - E_ex )
       function I_syn_inh pA = convolve(g_in, spikesInh) * ( V_m - E_in )
       function I_L pA = g_L * ( V_m - E_L )
       function I_sfa pA = g_sfa * ( V_m - E_sfa )
       function I_rr pA = g_rr * ( V_m - E_rr )

       V_m' = ( -I_L + I_e + I_stim - I_syn_exc - I_syn_inh - I_sfa - I_rr ) / C_m
     end

     parameters:
       V_th mV = -57.0 mV      # Threshold Potential
       V_reset mV = -70.0 mV   # Reset Potential
       t_ref ms = 0.5 ms       # Refractory period
       g_L nS = 28.95 nS       # Leak Conductance
       C_m pF = 289.5 pF       # Membrane Capacitance
       E_ex mV = 0 mV          # Excitatory reversal Potential
       E_in mV = -75.0 mV      # Inhibitory reversal Potential
       E_L mV = -70.0 mV       # Leak reversal Potential (aka resting potential)
       tau_syn_ex ms = 1.5 ms  # Synaptic Time Constant Excitatory Synapse
       tau_syn_in ms = 10.0 ms # Synaptic Time Constant for Inhibitory Synapse
       q_sfa nS = 14.48 nS     # Outgoing spike activated quantal spike-frequency adaptation conductance increase
       q_rr nS = 3214.0 nS     # Outgoing spike activated quantal relative refractory conductance increase.
       tau_sfa ms = 110.0 ms   # Time constant of spike-frequency adaptation.
       tau_rr ms = 1.97 ms     # Time constant of the relative refractory mechanism.
       E_sfa mV = -70.0 mV     # spike-frequency adaptation conductance reversal potential
       E_rr mV = -70.0 mV      # relative refractory mechanism conductance reversal potential

       # constant external input current
       I_e pA = 0 pA
     end

     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end

     input:
       spikesInh nS <- inhibitory spike
       spikesExc nS <- excitatory spike
       I_stim pA <- current
     end

     output: spike

     update:
       integrate_odes()
       if r != 0:  # neuron is absolute refractory
         r =  r - 1
         V_m = V_reset # clamp potential
       elif V_m >= V_th: # neuron is not absolute refractory
         r = RefractoryCounts
         V_m = V_reset # clamp potential
         g_sfa += q_sfa
         g_rr += q_rr
         emit_spike()
       end

     end

   end

   """
   Name: iaf_cond_exp_sfa_rr_implicit - Simple conductance based leaky integrate-and-fire
                               neuron model.

   Description:
   iaf_cond_exp_sfa_rr is an iaf_cond_exp_sfa_rr i.e. an implementation of a
   spiking neuron using IAF dynamics with conductance-based synapses,
   with additional spike-frequency adaptation and relative refractory
   mechanisms as described in Dayan+Abbott, 2001, page 166.

   As for the iaf_cond_exp_sfa_rr, Incoming spike events induce a post-synaptic
   change  of  conductance  modelled  by an  exponential  function.  The
   exponential function is  normalised such that an event  of weight 1.0
   results in a peak current of 1 nS.

   Outgoing spike events induce a change of the adaptation and relative
   refractory conductances by q_sfa and q_rr, respectively.  Otherwise
   these conductances decay exponentially with time constants tau_sfa
   and tau_rr, respectively.

   Sends: SpikeEvent

   Receives: SpikeEvent, CurrentEvent, DataLoggingRequest


   References:

   Meffin, H., Burkitt, A. N., & Grayden, D. B. (2004). An analytical
   model for the large, fluctuating synaptic conductance state typical of
   neocortical neurons in vivo. J.  Comput. Neurosci., 16, 159-175.

   Dayan, P. and Abbott, L. F. (2001). Theoretical Neuroscience, MIT Press (p166)

   Author: Sven Schrader, Eilif Muller

   SeeAlso: iaf_cond_exp_sfa_rr, aeif_cond_alpha, iaf_psc_delta, iaf_psc_exp,
   iaf_cond_alpha
   """
   neuron iaf_cond_exp_sfa_rr_implicit:

     initial_values:
       V_m mV = E_L      # membrane potential
       g_in nS  = 1 nS    # inputs from the inh conductance
       g_ex nS  = 1 nS    # inputs from the exc conductance
       g_sfa nS = 0 nS    # inputs from the sfa conductance
       g_rr nS  = 0 nS    # inputs from the rr conductance
     end

     state:
       r integer    # counts number of tick during the refractory period
     end

     equations:
       shape g_in' = -g_in/tau_syn_in
       shape g_ex' = -g_ex/tau_syn_ex

       g_sfa' = -g_sfa / tau_sfa
       g_rr' = -g_rr / tau_rr

       function I_syn_exc pA = convolve(g_ex, spikesExc) * ( V_m - E_ex )
       function I_syn_inh pA = convolve(g_in, spikesInh) * ( V_m - E_in )
       function I_L pA = g_L * ( V_m - E_L )
       function I_sfa pA = g_sfa * ( V_m - E_sfa )
       function I_rr pA = g_rr * ( V_m - E_rr )

       V_m' = ( -I_L + I_e + I_stim - I_syn_exc - I_syn_inh - I_sfa - I_rr ) / C_m
     end

     parameters:
       V_th mV = -57.0 mV      # Threshold Potential
       V_reset mV = -70.0 mV   # Reset Potential
       t_ref ms = 0.5 ms       # Refractory period
       g_L nS = 28.95 nS       # Leak Conductance
       C_m pF = 289.5 pF       # Membrane Capacitance
       E_ex mV = 0 mV         # Excitatory reversal Potential
       E_in mV = -75.0 mV      # Inhibitory reversal Potential
       E_L mV = -70.0 mV       # Leak reversal Potential (aka resting potential)
       tau_syn_ex ms = 1.5 ms  # Synaptic Time Constant Excitatory Synapse
       tau_syn_in ms = 10.0 ms # Synaptic Time Constant for Inhibitory Synapse
       q_sfa nS = 14.48 nS     # Outgoing spike activated quantal spike-frequency adaptation conductance increase
       q_rr nS = 3214.0 nS     # Outgoing spike activated quantal relative refractory conductance increase.
       tau_sfa ms = 110.0 ms   # Time constant of spike-frequency adaptation.
       tau_rr ms = 1.97 ms     # Time constant of the relative refractory mechanism.
       E_sfa mV = -70.0 mV     # spike-frequency adaptation conductance reversal potential
       E_rr mV = -70.0 mV      # relative refractory mechanism conductance reversal potential

       # constant external input current
       I_e pA = 0 pA
     end

     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end

     input:
       spikesInh nS <- inhibitory spike
       spikesExc nS <- excitatory spike
       I_stim pA <- current
     end

     output: spike

     update:
       integrate_odes()
       if r != 0:  # neuron is absolute refractory
         r =  r - 1
         V_m = V_reset # clamp potential
       elif V_m >= V_th: # neuron is not absolute refractory
         r = RefractoryCounts
         V_m = V_reset # clamp potential
         g_sfa += q_sfa
         g_rr += q_rr
         emit_spike()
       end

     end

   end




.. footer::

   Generated at 2020-02-21 10:47:40.888319
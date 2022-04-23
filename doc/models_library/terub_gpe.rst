terub_gpe
#########


terub_gpe - Terman Rubin neuron model

Description
+++++++++++

terub_gpe is an implementation of a spiking neuron using the Terman Rubin model
based on the Hodgkin-Huxley formalism.

(1) **Post-syaptic currents:** Incoming spike events induce a post-synaptic change of current modelled
    by an alpha function. The alpha function is normalised such that an event of
    weight 1.0 results in a peak current of 1 pA.

(2) **Spike Detection:** Spike detection is done by a combined threshold-and-local-maximum search: if there
    is a local maximum above a certain threshold of the membrane potential, it is considered a spike.

References
++++++++++

.. [1] Terman, D. and Rubin, J.E. and Yew, A. C. and Wilson, C.J.
       Activity Patterns in a Model for the Subthalamopallidal Network
       of the Basal Ganglia
       The Journal of Neuroscience, 22(7), 2963-2976 (2002)

.. [2] Rubin, J.E. and Terman, D.
       High Frequency Stimulation of the Subthalamic Nucleus Eliminates
       Pathological Thalamic Rhythmicity in a Computational Model
       Journal of Computational Neuroscience, 16, 211-235 (2004)



Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "E_L", "mV", "-55mV", "Resting membrane potential"    
    "g_L", "nS", "0.1nS", "Leak conductance"    
    "C_m", "pF", "1pF", "Capacitance of the membrane"    
    "E_Na", "mV", "55mV", "Sodium reversal potential"    
    "g_Na", "nS", "120nS", "Sodium peak conductance"    
    "E_K", "mV", "-80.0mV", "Potassium reversal potential"    
    "g_K", "nS", "30.0nS", "Potassium peak conductance"    
    "E_Ca", "mV", "120mV", "Calcium reversal potential"    
    "g_Ca", "nS", "0.15nS", "Calcium peak conductance"    
    "g_T", "nS", "0.5nS", "T-type Calcium channel peak conductance"    
    "g_ahp", "nS", "30nS", "Afterpolarization current peak conductance"    
    "tau_syn_exc", "ms", "1ms", "Rise time of the excitatory synaptic alpha function"    
    "tau_syn_inh", "ms", "12.5ms", "Rise time of the inhibitory synaptic alpha function"    
    "E_gg", "mV", "-100mV", "Reversal potential for inhibitory input (from GPe)"    
    "t_ref", "ms", "2ms", "Refractory time"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "counts number of ticks during the refractory period"    
    "V_m", "mV", "E_L", "Membrane potential"    
    "gate_h", "real", "0.0", "gating variable h"    
    "gate_n", "real", "0.0", "gating variable n"    
    "gate_r", "real", "0.0", "gating variable r"    
    "Ca_con", "real", "0.0", "gating variable r"




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-(I_{Na} + I_{K} + I_{L} + I_{T} + I_{Ca} + I_{ahp}) \cdot \mathrm{pA} + I_{e} + I_{stim} + I_{exc,mod} \cdot \mathrm{pA} + I_{inh,mod} \cdot \mathrm{pA}) } \right) 


.. math::
   \frac{ dgate_{h} } { dt }= \frac 1 { \mathrm{ms} } \left( { g_{\phi,h} \cdot (\frac{ (h_{\infty} - gate_{h}) } { \tau_{h} }) } \right) 


.. math::
   \frac{ dgate_{n} } { dt }= \frac 1 { \mathrm{ms} } \left( { g_{\phi,n} \cdot (\frac{ (n_{\infty} - gate_{n}) } { \tau_{n} }) } \right) 


.. math::
   \frac{ dgate_{r} } { dt }= \frac 1 { \mathrm{ms} } \left( { g_{\phi,r} \cdot (\frac{ (r_{\infty} - gate_{r}) } { \tau_{r} }) } \right) 


.. math::
   \frac{ dCa_{con} } { dt }= g_{\epsilon} \cdot (-I_{Ca} - I_{T} - g_{k,Ca} \cdot Ca_{con})





Source code
+++++++++++

.. code-block:: nestml

   neuron terub_gpe:
     state:
       r integer = 0 # counts number of ticks during the refractory period
       V_m mV = E_L # Membrane potential
       gate_h real = 0.0 # gating variable h
       gate_n real = 0.0 # gating variable n
       gate_r real = 0.0 # gating variable r
       Ca_con real = 0.0 # gating variable r
     end
     equations:
       # Parameters for Terman Rubin GPe Neuron
       inline g_tau_n_0 ms = 0.05ms
       inline g_tau_n_1 ms = 0.27ms
       inline g_theta_n_tau mV = -40.0mV
       inline g_sigma_n_tau mV = -12.0mV
       inline g_tau_h_0 ms = 0.05ms
       inline g_tau_h_1 ms = 0.27ms
       inline g_theta_h_tau mV = -40.0mV
       inline g_sigma_h_tau mV = -12.0mV
       inline g_tau_r ms = 30.0ms
       # steady state values for gating variables
       inline g_theta_a mV = -57.0mV
       inline g_sigma_a mV = 2.0mV
       inline g_theta_h mV = -58.0mV
       inline g_sigma_h mV = -12.0mV
       inline g_theta_m mV = -37.0mV
       inline g_sigma_m mV = 10.0mV
       inline g_theta_n mV = -50.0mV
       inline g_sigma_n mV = 14.0mV
       inline g_theta_r mV = -70.0mV
       inline g_sigma_r mV = -2.0mV
       inline g_theta_s mV = -35.0mV
       inline g_sigma_s mV = 2.0mV
       # time evolvement of gating variables
       inline g_phi_h real = 0.05
       inline g_phi_n real = 0.1 # Report: 0.1, Terman Rubin 2002: 0.05
       inline g_phi_r real = 1.0
       # Calcium concentration and afterhyperpolarization current
       inline g_epsilon 1/ms = 0.0001 / ms
       inline g_k_Ca real = 15.0 # Report:15,  Terman Rubin 2002: 20.0
       inline g_k1 real = 30.0
       inline I_exc_mod real = -convolve(g_exc,exc_spikes) * V_m
       inline I_inh_mod real = convolve(g_inh,inh_spikes) * (V_m - E_gg)
       inline tau_n real = g_tau_n_0 + g_tau_n_1 / (1.0 + exp(-(V_m - g_theta_n_tau) / g_sigma_n_tau))
       inline tau_h real = g_tau_h_0 + g_tau_h_1 / (1.0 + exp(-(V_m - g_theta_h_tau) / g_sigma_h_tau))
       inline tau_r real = g_tau_r
       inline a_inf real = 1.0 / (1.0 + exp(-(V_m - g_theta_a) / g_sigma_a))
       inline h_inf real = 1.0 / (1.0 + exp(-(V_m - g_theta_h) / g_sigma_h))
       inline m_inf real = 1.0 / (1.0 + exp(-(V_m - g_theta_m) / g_sigma_m))
       inline n_inf real = 1.0 / (1.0 + exp(-(V_m - g_theta_n) / g_sigma_n))
       inline r_inf real = 1.0 / (1.0 + exp(-(V_m - g_theta_r) / g_sigma_r))
       inline s_inf real = 1.0 / (1.0 + exp(-(V_m - g_theta_s) / g_sigma_s))
       inline I_Na real = g_Na * m_inf * m_inf * m_inf * gate_h * (V_m - E_Na)
       inline I_K real = g_K * gate_n * gate_n * gate_n * gate_n * (V_m - E_K)
       inline I_L real = g_L * (V_m - E_L)
       inline I_T real = g_T * a_inf * a_inf * a_inf * gate_r * (V_m - E_Ca)
       inline I_Ca real = g_Ca * s_inf * s_inf * (V_m - E_Ca)
       inline I_ahp real = g_ahp * (Ca_con / (Ca_con + g_k1)) * (V_m - E_K)
       # synapses: alpha functions
       # alpha function for the g_inh
       kernel g_inh = (e / tau_syn_inh) * t * exp(-t / tau_syn_inh)
       # alpha function for the g_exc

       # alpha function for the g_exc
       kernel g_exc = (e / tau_syn_exc) * t * exp(-t / tau_syn_exc)
       # V dot -- synaptic input are currents, inhib current is negative
       V_m'=(-(I_Na + I_K + I_L + I_T + I_Ca + I_ahp) * pA + I_e + I_stim + I_exc_mod * pA + I_inh_mod * pA) / C_m
       # channel dynamics
       gate_h'=g_phi_h * ((h_inf - gate_h) / tau_h) / ms # h-variable
       gate_n'=g_phi_n * ((n_inf - gate_n) / tau_n) / ms # n-variable
       gate_r'=g_phi_r * ((r_inf - gate_r) / tau_r) / ms # r-variable
       # Calcium concentration

       # Calcium concentration
       Ca_con'=g_epsilon * (-I_Ca - I_T - g_k_Ca * Ca_con)
     end

     parameters:
       E_L mV = -55mV # Resting membrane potential
       g_L nS = 0.1nS # Leak conductance
       C_m pF = 1pF # Capacitance of the membrane
       E_Na mV = 55mV # Sodium reversal potential
       g_Na nS = 120nS # Sodium peak conductance
       E_K mV = -80.0mV # Potassium reversal potential
       g_K nS = 30.0nS # Potassium peak conductance
       E_Ca mV = 120mV # Calcium reversal potential
       g_Ca nS = 0.15nS # Calcium peak conductance
       g_T nS = 0.5nS # T-type Calcium channel peak conductance
       g_ahp nS = 30nS # Afterpolarization current peak conductance
       tau_syn_exc ms = 1ms # Rise time of the excitatory synaptic alpha function
       tau_syn_inh ms = 12.5ms # Rise time of the inhibitory synaptic alpha function
       E_gg mV = -100mV # Reversal potential for inhibitory input (from GPe)
       t_ref ms = 2ms # Refractory time
       # constant external input current

       # constant external input current
       I_e pA = 0pA
     end
     internals:
       refractory_counts integer = steps(t_ref)
     end
     input:
       inh_spikes nS <-inhibitory spike
       exc_spikes nS <-excitatory spike
       I_stim pA <-current
     end

     output: spike

     update:
       U_old mV = V_m
       integrate_odes()
       # sending spikes: crossing 0 mV, pseudo-refractoriness and local maximum...
       if r > 0:
         r -= 1
       elif V_m > 0mV and U_old > V_m:
         r = refractory_counts
         emit_spike()
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: terub_gpe_characterisation.rst


.. footer::

   Generated at 2022-03-28 19:04:28.746026
terub_stn
#########

terub_stn - Terman Rubin neuron model


Description
+++++++++++

terub_stn is an implementation of a spiking neuron using the Terman Rubin model
based on the Hodgkin-Huxley formalism.

(1) **Post-syaptic currents:** Incoming spike events induce a post-synaptic change of current modelled
    by an alpha function. The alpha function is normalised such that an event of
    weight 1.0 results in a peak current of 1 pA.

(2) **Spike Detection:** Spike detection is done by a combined threshold-and-local-maximum search: if there
    is a local maximum above a certain threshold of the membrane potential, it is considered a spike.


References
++++++++++

.. [1] Terman, D. and Rubin, J.E. and Yew, A.C. and Wilson, C.J. Activity Patterns in a Model for the Subthalamopallidal Network
       of the Basal Ganglia. The Journal of Neuroscience, 22(7), 2963-2976 (2002)

.. [2] Rubin, J.E. and Terman, D. High Frequency Stimulation of the Subthalamic Nucleus Eliminates
       Pathological Thalamic Rhythmicity in a Computational Model Journal of Computational Neuroscience, 16, 211-235 (2004)


Author
++++++

Martin Ebert


Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "E_L", "mV", "-60mV", "Resting membrane potential."    
    "g_L", "nS", "2.25nS", "Leak conductance."    
    "C_m", "pF", "1.0pF", "Capacity of the membrane."    
    "E_Na", "mV", "55mV", "Sodium reversal potential."    
    "g_Na", "nS", "37.5nS", "Sodium peak conductance."    
    "E_K", "mV", "-80.0mV", "Potassium reversal potential."    
    "g_K", "nS", "45.0nS", "Potassium peak conductance."    
    "E_Ca", "mV", "120mV", "Calcium reversal potential."    
    "g_Ca", "nS", "140nS", "Calcium peak conductance."    
    "g_T", "nS", "0.5nS", "T-type Calcium channel peak conductance."    
    "g_ahp", "nS", "9nS", "afterpolarization current peak conductance."    
    "tau_syn_ex", "ms", "1.0ms", "Rise time of the excitatory synaptic alpha function."    
    "tau_syn_in", "ms", "0.08ms", "Rise time of the inhibitory synaptic alpha function."    
    "E_gs", "mV", "-85.0mV", "reversal potential for inhibitory input (from GPe)"    
    "t_ref", "ms", "2ms", "refractory time"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "E_L", "Membrane potential"    
    "gate_h", "real", "0.0", "gating variable h"    
    "gate_n", "real", "0.0", "gating variable n"    
    "gate_r", "real", "0.0", "gating variable r"    
    "Ca_con", "real", "0.0", "gating variable r"




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-(I_{Na} + I_{K} + I_{L} + I_{T} + I_{Ca} + I_{ahp}) + I_{e} + I_{stim} + I_{ex,mod} + I_{in,mod}) } \right) 


.. math::
   \frac{ dgate_{h} } { dt }= \phi_{h} \cdot (\frac{ (h_{\infty} - gate_{h}) } { \tau_{h} })


.. math::
   \frac{ dgate_{n} } { dt }= \phi_{n} \cdot (\frac{ (n_{\infty} - gate_{n}) } { \tau_{n} })


.. math::
   \frac{ dgate_{r} } { dt }= \phi_{r} \cdot (\frac{ (r_{\infty} - gate_{r}) } { \tau_{r} })


.. math::
   \frac{ dCa_{con} } { dt }= \epsilon \cdot (\frac{ (-I_{Ca} - I_{T}) } { \mathrm{pA} } - k_{Ca} \cdot Ca_{con})





Source code
+++++++++++

.. code:: nestml

   neuron terub_stn:
     state:
       r integer  # counts number of tick during the refractory period
     end
     initial_values:
       V_m mV = E_L # Membrane potential
       gate_h real = 0.0 # gating variable h
       gate_n real = 0.0 # gating variable n
       gate_r real = 0.0 # gating variable r
       Ca_con real = 0.0 # gating variable r
     end
     equations:

       /*time constants for slow gating variables*/
       function tau_n_0 ms = 1.0ms
       function tau_n_1 ms = 100.0ms
       function theta_n_tau mV = -80.0mV
       function sigma_n_tau mV = -26.0mV
       function tau_h_0 ms = 1.0ms
       function tau_h_1 ms = 500.0ms
       function theta_h_tau mV = -57.0mV
       function sigma_h_tau mV = -3.0mV
       function tau_r_0 ms = 7.1ms # Guo 7.1 Terman02 40.0
       function tau_r_1 ms = 17.5ms
       function theta_r_tau mV = 68.0mV
       function sigma_r_tau mV = -2.2mV

       /*steady state values for gating variables*/
       function theta_a mV = -63.0mV
       function sigma_a mV = 7.8mV
       function theta_h mV = -39.0mV
       function sigma_h mV = -3.1mV
       function theta_m mV = -30.0mV
       function sigma_m mV = 15.0mV
       function theta_n mV = -32.0mV
       function sigma_n mV = 8.0mV
       function theta_r mV = -67.0mV
       function sigma_r mV = -2.0mV
       function theta_s mV = -39.0mV
       function sigma_s mV = 8.0mV
       function theta_b real = 0.25 # Guo 0.25 Terman02 0.4
       function sigma_b real = 0.07 # Guo 0.07 Terman02 -0.1

       /*time evolvement of gating variables*/
       function phi_h real = 0.75
       function phi_n real = 0.75
       function phi_r real = 0.5 # Guo 0.5 Terman02 0.2

       /* Calcium concentration and afterhyperpolarization current*/
       function epsilon 1/ms = 5e-05 / ms # 1/ms Guo 0.00005 Terman02 0.0000375
       function k_Ca real = 22.5
       function k1 real = 15.0
       function I_ex_mod pA = -convolve(g_ex,spikeExc) * V_m
       function I_in_mod pA = convolve(g_in,spikeInh) * (V_m - E_gs)
       function tau_n ms = tau_n_0 + tau_n_1 / (1.0 + exp(-(V_m - theta_n_tau) / sigma_n_tau))
       function tau_h ms = tau_h_0 + tau_h_1 / (1.0 + exp(-(V_m - theta_h_tau) / sigma_h_tau))
       function tau_r ms = tau_r_0 + tau_r_1 / (1.0 + exp(-(V_m - theta_r_tau) / sigma_r_tau))
       function a_inf real = 1.0 / (1.0 + exp(-(V_m - theta_a) / sigma_a))
       function h_inf real = 1.0 / (1.0 + exp(-(V_m - theta_h) / sigma_h))
       function m_inf real = 1.0 / (1.0 + exp(-(V_m - theta_m) / sigma_m))
       function n_inf real = 1.0 / (1.0 + exp(-(V_m - theta_n) / sigma_n))
       function r_inf real = 1.0 / (1.0 + exp(-(V_m - theta_r) / sigma_r))
       function s_inf real = 1.0 / (1.0 + exp(-(V_m - theta_s) / sigma_s))
       function b_inf real = 1.0 / (1.0 + exp((gate_r - theta_b) / sigma_b)) - 1.0 / (1.0 + exp(-theta_b / sigma_b))
       function I_Na pA = g_Na * m_inf * m_inf * m_inf * gate_h * (V_m - E_Na)
       function I_K pA = g_K * gate_n * gate_n * gate_n * gate_n * (V_m - E_K)
       function I_L pA = g_L * (V_m - E_L)
       function I_T pA = g_T * a_inf * a_inf * a_inf * b_inf * b_inf * (V_m - E_Ca)
       function I_Ca pA = g_Ca * s_inf * s_inf * (V_m - E_Ca)
       function I_ahp pA = g_ahp * (Ca_con / (Ca_con + k1)) * (V_m - E_K)

       /* V dot -- synaptic input are currents, inhib current is negative*/
       V_m'=(-(I_Na + I_K + I_L + I_T + I_Ca + I_ahp) + I_e + I_stim + I_ex_mod + I_in_mod) / C_m

       /*channel dynamics*/
       gate_h'=phi_h * ((h_inf - gate_h) / tau_h) # h-variable
       gate_n'=phi_n * ((n_inf - gate_n) / tau_n) # n-variable
       gate_r'=phi_r * ((r_inf - gate_r) / tau_r) # r-variable

       /*Calcium concentration*/
       Ca_con'=epsilon * ((-I_Ca - I_T) / pA - k_Ca * Ca_con)

       /* synapses: alpha functions*/
       /* alpha function for the g_in*/
       kernel g_in = (e / tau_syn_in) * t * exp(-t / tau_syn_in)
       /* alpha function for the g_ex*/

       /* alpha function for the g_ex*/
       kernel g_ex = (e / tau_syn_ex) * t * exp(-t / tau_syn_ex)
     end

     parameters:
       E_L mV = -60mV # Resting membrane potential.
       g_L nS = 2.25nS # Leak conductance.
       C_m pF = 1.0pF # Capacity of the membrane.
       E_Na mV = 55mV # Sodium reversal potential.
       g_Na nS = 37.5nS # Sodium peak conductance.
       E_K mV = -80.0mV # Potassium reversal potential.
       g_K nS = 45.0nS # Potassium peak conductance.
       E_Ca mV = 120mV # Calcium reversal potential.
       g_Ca nS = 140nS # Calcium peak conductance.
       g_T nS = 0.5nS # T-type Calcium channel peak conductance.
       g_ahp nS = 9nS # afterpolarization current peak conductance.
       tau_syn_ex ms = 1.0ms # Rise time of the excitatory synaptic alpha function.
       tau_syn_in ms = 0.08ms # Rise time of the inhibitory synaptic alpha function.
       E_gs mV = -85.0mV # reversal potential for inhibitory input (from GPe)
       t_ref ms = 2ms # refractory time

       /* constant external input current*/
       I_e pA = 0pA
     end
     internals:
       refractory_counts integer = steps(t_ref)
     end
     input:
       spikeInh nS <-inhibitory spike
       spikeExc nS <-excitatory spike
       I_stim pA <-current
     end

     output: spike

     update:
       U_old mV = V_m
       integrate_odes()

       /* sending spikes: crossing 0 mV, pseudo-refractoriness and local maximum...*/
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

.. include:: terub_stn_characterisation.rst


.. footer::

   Generated at 2020-05-27 18:26:45.236576
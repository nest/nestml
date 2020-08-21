hill_tononi
###########

hill_tononi - Neuron model after Hill & Tononi (2005)


Description
+++++++++++

This model neuron implements a slightly modified version of the
neuron model described in [1]_. The most important properties are:

- Integrate-and-fire with threshold adaptive threshold.
- Repolarizing potassium current instead of hard reset.
- AMPA, NMDA, GABA_A, and GABA_B conductance-based synapses with
  beta-function (difference of exponentials) time course.
- Voltage-dependent NMDA with instantaneous or two-stage unblocking [1]_, [2]_.
- Intrinsic currents I_h, I_T, I_Na(p), and I_KNa.
- Synaptic "minis" are not implemented.

Documentation and examples can be found on the NEST Simulator repository
(https://github.com/nest/nest-simulator/) at the following paths:
- docs/model_details/HillTononiModels.ipynb
- pynest/examples/intrinsic_currents_spiking.py
- pynest/examples/intrinsic_currents_subthreshold.py


References
++++++++++

.. [1] Hill S, Tononi G (2005). Modeling sleep and wakefulness in the
       thalamocortical system. Journal of Neurophysiology. 93:1671-1698.
       DOI: https://doi.org/10.1152/jn.00915.2004
.. [2] Vargas-Caballero M, Robinson HPC (2003). A slow fraction of Mg2+
       unblock of NMDA receptors limits their  contribution to spike generation
       in cortical pyramidal neurons. Journal of Neurophysiology 89:2778-2783.
       DOI: https://doi.org/10.1152/jn.01038.2002

Author
++++++

Hans Ekkehard Plesser


Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "E_Na", "mV", "30.0mV", ""    
    "E_K", "mV", "-90.0mV", ""    
    "g_NaL", "nS", "0.2nS", ""    
    "g_KL", "nS", "1.0nS", "1.0 - 1.85"    
    "Tau_m", "ms", "16.0ms", "membrane time constant applying to all currents but repolarizing K-current (see [1, p 1677])"    
    "Theta_eq", "mV", "-51.0mV", "equilibrium value"    
    "Tau_theta", "ms", "2.0ms", "time constant"    
    "Tau_spike", "ms", "1.75ms", "membrane time constant applying to repolarizing K-current"    
    "t_spike", "ms", "2.0ms", "duration of re-polarizing potassium current"    
    "AMPA_g_peak", "nS", "0.1nS", "Parameters for synapse of type AMPA, GABA_A, GABA_B and NMDApeak conductance"    
    "AMPA_E_rev", "mV", "0.0mV", "reversal potential"    
    "AMPA_Tau_1", "ms", "0.5ms", "rise time"    
    "AMPA_Tau_2", "ms", "2.4ms", "decay time, Tau_1 < Tau_2"    
    "NMDA_g_peak", "nS", "0.075nS", "peak conductance"    
    "NMDA_Tau_1", "ms", "4.0ms", "rise time"    
    "NMDA_Tau_2", "ms", "40.0ms", "decay time, Tau_1 < Tau_2"    
    "NMDA_E_rev", "mV", "0.0mV", "reversal potential"    
    "NMDA_Vact", "mV", "-58.0mV", "inactive for V << Vact, inflection of sigmoid"    
    "NMDA_Sact", "mV", "2.5mV", "scale of inactivation"    
    "GABA_A_g_peak", "nS", "0.33nS", "peak conductance"    
    "GABA_A_Tau_1", "ms", "1.0ms", "rise time"    
    "GABA_A_Tau_2", "ms", "7.0ms", "decay time, Tau_1 < Tau_2"    
    "GABA_A_E_rev", "mV", "-70.0mV", "reversal potential"    
    "GABA_B_g_peak", "nS", "0.0132nS", "peak conductance"    
    "GABA_B_Tau_1", "ms", "60.0ms", "rise time"    
    "GABA_B_Tau_2", "ms", "200.0ms", "decay time, Tau_1 < Tau_2"    
    "GABA_B_E_rev", "mV", "-90.0mV", "reversal potential for intrinsic current"    
    "NaP_g_peak", "nS", "1.0nS", "parameters for intrinsic currentspeak conductance for intrinsic current"    
    "NaP_E_rev", "mV", "30.0mV", "reversal potential for intrinsic current"    
    "KNa_g_peak", "nS", "1.0nS", "peak conductance for intrinsic current"    
    "KNa_E_rev", "mV", "-90.0mV", "reversal potential for intrinsic current"    
    "T_g_peak", "nS", "1.0nS", "peak conductance for intrinsic current"    
    "T_E_rev", "mV", "0.0mV", "reversal potential for intrinsic current"    
    "h_g_peak", "nS", "1.0nS", "peak conductance for intrinsic current"    
    "h_E_rev", "mV", "-40.0mV", "reversal potential for intrinsic current"    
    "KNa_D_EQ", "pA", "0.001pA", ""    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "(g_NaL * E_Na + g_KL * E_K) / (g_NaL + g_KL)", "membrane potential"    
    "Theta", "mV", "Theta_eq", "Threshold"    
    "g_AMPA", "nS", "0.0nS", ""    
    "g_NMDA", "nS", "0.0nS", ""    
    "g_GABAA", "nS", "0.0nS", ""    
    "g_GABAB", "nS", "0.0nS", ""    
    "IKNa_D", "nS", "0.0nS", ""    
    "g_AMPA__d", "nS / ms", "0.0nS / ms", ""    
    "g_NMDA__d", "nS / ms", "0.0nS / ms", ""    
    "g_GABAA__d", "nS / ms", "0.0nS / ms", ""    
    "g_GABAB__d", "nS / ms", "0.0nS / ms", ""    
    "IT_m", "real", "0.0", ""    
    "IT_h", "real", "0.0", ""    
    "Ih_m", "real", "0.0", ""




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { \mathrm{nF} } \left( { (\frac 1 { \Tau_{m} } \left( { (I_{Na} + I_{K} + I_{syn} + I_{NaP} + I_{KNa} + I_{T} + I_{h} + I_{e} + I_{stim}) } \right)  + \frac{ I_{spike} } { (\mathrm{ms} \cdot \mathrm{mV}) }) \cdot \mathrm{s} } \right) 


.. math::
   \frac{ d\Theta } { dt }= \frac{ -(\Theta - \Theta_{eq}) } { \Tau_{\theta} }


.. math::
   \frac{ dIKNa_{D} } { dt }= \frac 1 { \mathrm{ms} } \left( { (D_{influx,peak} \cdot D_{influx} \cdot \mathrm{nS} - \frac 1 { \tau_{D} } \left( { (IKNa_{D} - \frac{ KNa_{D,EQ} } { \mathrm{mV} }) } \right) ) } \right) 


.. math::
   \frac{ dIT_{m} } { dt }= \frac{ (m_{\infty,T} - IT_{m}) } { \tau_{m,T} }


.. math::
   \frac{ dIT_{h} } { dt }= \frac{ (h_{\infty,T} - IT_{h}) } { \tau_{h,T} }


.. math::
   \frac{ dIh_{m} } { dt }= \frac{ (m_{\infty,h} - Ih_{m}) } { \tau_{m,h} }


.. math::
   \frac{ dg_{AMPA,,d} } { dt }= \frac{ -g_{AMPA,,d} } { AMPA_{\Tau,1} }


.. math::
   \frac{ dg_{AMPA} } { dt }= g_{AMPA,,d} - \frac{ g_{AMPA} } { AMPA_{\Tau,2} }


.. math::
   \frac{ dg_{NMDA,,d} } { dt }= \frac{ -g_{NMDA,,d} } { NMDA_{\Tau,1} }


.. math::
   \frac{ dg_{NMDA} } { dt }= g_{NMDA,,d} - \frac{ g_{NMDA} } { NMDA_{\Tau,2} }


.. math::
   \frac{ dg_{GABAA,,d} } { dt }= \frac{ -g_{GABAA,,d} } { GABA_{A,\Tau,1} }


.. math::
   \frac{ dg_{GABAA} } { dt }= g_{GABAA,,d} - \frac{ g_{GABAA} } { GABA_{A,\Tau,2} }


.. math::
   \frac{ dg_{GABAB,,d} } { dt }= \frac{ -g_{GABAB,,d} } { GABA_{B,\Tau,1} }


.. math::
   \frac{ dg_{GABAB} } { dt }= g_{GABAB,,d} - \frac{ g_{GABAB} } { GABA_{B,\Tau,2} }





Source code
+++++++++++

.. code:: nestml

   neuron hill_tononi:
     state:
       r_potassium integer 
       g_spike boolean = false
     end
     initial_values:
       V_m mV = (g_NaL * E_Na + g_KL * E_K) / (g_NaL + g_KL) # membrane potential
       Theta mV = Theta_eq # Threshold
       g_AMPA,g_NMDA,g_GABAA,g_GABAB,IKNa_D nS = 0.0nS
       g_AMPA__d,g_NMDA__d,g_GABAA__d,g_GABAB__d nS/ms = 0.0nS / ms
       IT_m,IT_h,Ih_m real = 0.0
     end
     equations:

       /**/
       /* V_m*/
       /**/
       function I_syn_ampa pA = -g_AMPA * (V_m - AMPA_E_rev)
       function I_syn_nmda pA = -g_NMDA * (V_m - NMDA_E_rev) / (1 + exp((NMDA_Vact - V_m) / NMDA_Sact))
       function I_syn_gaba_a pA = -g_GABAA * (V_m - GABA_A_E_rev)
       function I_syn_gaba_b pA = -g_GABAB * (V_m - GABA_B_E_rev)
       function I_syn pA = I_syn_ampa + I_syn_nmda + I_syn_gaba_a + I_syn_gaba_b
       function I_Na pA = -g_NaL * (V_m - E_Na)
       function I_K pA = -g_KL * (V_m - E_K)

       /* I_Na(p), m_inf^3 according to Compte et al, J Neurophysiol 2003 89:2707*/
       function INaP_thresh mV = -55.7mV
       function INaP_slope mV = 7.7mV
       function m_inf_NaP real = 1.0 / (1.0 + exp(-(V_m - INaP_thresh) / INaP_slope))
       function d_half real = 0.25
       function m_inf_KNa real = 1.0 / (1.0 + (d_half / (IKNa_D / nS)) ** 3.5)

       /* Persistent Na current; member only to allow recording*/
   recordable    function I_NaP pA = -NaP_g_peak * m_inf_NaP ** 3 * (V_m - NaP_E_rev)

       /* Depol act. K current; member only to allow recording*/
   recordable    function I_KNa pA = -KNa_g_peak * m_inf_KNa * (V_m - KNa_E_rev)

       /* Low-thresh Ca current; member only to allow recording*/
   recordable    function I_T pA = -T_g_peak * IT_m * IT_m * IT_h * (V_m - T_E_rev)
   recordable    function I_h pA = -h_g_peak * Ih_m * (V_m - h_E_rev)

       /* The spike current is only activate immediately after a spike.*/
       function I_spike pA = (g_spike)?-(V_m - E_K) / Tau_spike / mV * ms * pA:0pA
       V_m'=((I_Na + I_K + I_syn + I_NaP + I_KNa + I_T + I_h + I_e + I_stim) / Tau_m + I_spike / (ms * mV)) * s / nF

       /**/
       /* Intrinsic currents*/
       /**/
       /* I_T*/
       function m_inf_T real = 1.0 / (1.0 + exp(-(V_m / mV + 59.0) / 6.2))
       function h_inf_T real = 1.0 / (1.0 + exp((V_m / mV + 83.0) / 4))
       /* I_KNa*/

       /* I_KNa*/
       function D_influx_peak real = 0.025
       function tau_D real = 1250.0 # yes, 1.25 s
       function D_thresh mV = -10.0mV
       function D_slope mV = 5.0mV
       function D_influx real = 1.0 / (1.0 + exp(-(V_m - D_thresh) / D_slope))
       Theta'=-(Theta - Theta_eq) / Tau_theta

       /* equation modified from y[](1-D_eq) to (y[]-D_eq), since we'd not*/
       /* be converging to equilibrium otherwise*/
       IKNa_D'=(D_influx_peak * D_influx * nS - (IKNa_D - KNa_D_EQ / mV) / tau_D) / ms
       function tau_m_T ms = (0.22 / (exp(-(V_m / mV + 132.0) / 16.7) + exp((V_m / mV + 16.8) / 18.2)) + 0.13) * ms
       function tau_h_T ms = (8.2 + (56.6 + 0.27 * exp((V_m / mV + 115.2) / 5.0)) / (1.0 + exp((V_m / mV + 86.0) / 3.2))) * ms
       function tau_m_h ms = (1.0 / (exp(-14.59 - 0.086 * V_m / mV) + exp(-1.87 + 0.0701 * V_m / mV))) * ms
       function I_h_Vthreshold real = -75.0
       function m_inf_h real = 1.0 / (1.0 + exp((V_m / mV - I_h_Vthreshold) / 5.5))
       IT_m'=(m_inf_T - IT_m) / tau_m_T
       IT_h'=(h_inf_T - IT_h) / tau_h_T
       Ih_m'=(m_inf_h - Ih_m) / tau_m_h

       /**/
       /* Synapses*/
       /**/
       g_AMPA__d'=-g_AMPA__d / AMPA_Tau_1
       g_AMPA'=g_AMPA__d - g_AMPA / AMPA_Tau_2
       g_NMDA__d'=-g_NMDA__d / NMDA_Tau_1
       g_NMDA'=g_NMDA__d - g_NMDA / NMDA_Tau_2
       g_GABAA__d'=-g_GABAA__d / GABA_A_Tau_1
       g_GABAA'=g_GABAA__d - g_GABAA / GABA_A_Tau_2
       g_GABAB__d'=-g_GABAB__d / GABA_B_Tau_1
       g_GABAB'=g_GABAB__d - g_GABAB / GABA_B_Tau_2
     end

     parameters:
       E_Na mV = 30.0mV
       E_K mV = -90.0mV
       g_NaL nS = 0.2nS
       g_KL nS = 1.0nS # 1.0 - 1.85
       Tau_m ms = 16.0ms # membrane time constant applying to all currents but repolarizing K-current (see [1, p 1677])
       Theta_eq mV = -51.0mV # equilibrium value
       Tau_theta ms = 2.0ms # time constant
       Tau_spike ms = 1.75ms # membrane time constant applying to repolarizing K-current
       t_spike ms = 2.0ms # duration of re-polarizing potassium current

       /* Parameters for synapse of type AMPA, GABA_A, GABA_B and NMDA*/
       AMPA_g_peak nS = 0.1nS # peak conductance
       AMPA_E_rev mV = 0.0mV # reversal potential
       AMPA_Tau_1 ms = 0.5ms # rise time
       AMPA_Tau_2 ms = 2.4ms # decay time, Tau_1 < Tau_2
       NMDA_g_peak nS = 0.075nS # peak conductance
       NMDA_Tau_1 ms = 4.0ms # rise time
       NMDA_Tau_2 ms = 40.0ms # decay time, Tau_1 < Tau_2
       NMDA_E_rev mV = 0.0mV # reversal potential
       NMDA_Vact mV = -58.0mV # inactive for V << Vact, inflection of sigmoid
       NMDA_Sact mV = 2.5mV # scale of inactivation
       GABA_A_g_peak nS = 0.33nS # peak conductance
       GABA_A_Tau_1 ms = 1.0ms # rise time
       GABA_A_Tau_2 ms = 7.0ms # decay time, Tau_1 < Tau_2
       GABA_A_E_rev mV = -70.0mV # reversal potential
       GABA_B_g_peak nS = 0.0132nS # peak conductance
       GABA_B_Tau_1 ms = 60.0ms # rise time
       GABA_B_Tau_2 ms = 200.0ms # decay time, Tau_1 < Tau_2
       GABA_B_E_rev mV = -90.0mV # reversal potential for intrinsic current

       /* parameters for intrinsic currents*/
       NaP_g_peak nS = 1.0nS # peak conductance for intrinsic current
       NaP_E_rev mV = 30.0mV # reversal potential for intrinsic current
       KNa_g_peak nS = 1.0nS # peak conductance for intrinsic current
       KNa_E_rev mV = -90.0mV # reversal potential for intrinsic current
       T_g_peak nS = 1.0nS # peak conductance for intrinsic current
       T_E_rev mV = 0.0mV # reversal potential for intrinsic current
       h_g_peak nS = 1.0nS # peak conductance for intrinsic current
       h_E_rev mV = -40.0mV # reversal potential for intrinsic current
       KNa_D_EQ pA = 0.001pA

       /* constant external input current*/
       I_e pA = 0pA
     end
     internals:
       AMPAInitialValue real = compute_synapse_constant(AMPA_Tau_1,AMPA_Tau_2,AMPA_g_peak)
       NMDAInitialValue real = compute_synapse_constant(NMDA_Tau_1,NMDA_Tau_2,NMDA_g_peak)
       GABA_AInitialValue real = compute_synapse_constant(GABA_A_Tau_1,GABA_A_Tau_2,GABA_A_g_peak)
       GABA_BInitialValue real = compute_synapse_constant(GABA_B_Tau_1,GABA_B_Tau_2,GABA_B_g_peak)
       PotassiumRefractoryCounts integer = steps(t_spike)
     end
     input:
       AMPA nS <-spike
       NMDA nS <-spike
       GABA_A nS <-spike
       GABA_B nS <-spike
       I_stim pA <-current
     end

     output: spike

     update:
       integrate_odes()

       /* Deactivate potassium current after spike time have expired*/
       if (r_potassium > 0) and (r_potassium - 1 == 0):
         g_spike = false # Deactivate potassium current.
       end
       r_potassium -= 1
       g_AMPA__d += AMPAInitialValue * AMPA / ms
       g_NMDA__d += NMDAInitialValue * NMDA / ms
       g_GABAA__d += GABA_AInitialValue * GABA_A / ms
       g_GABAB__d += GABA_BInitialValue * GABA_B / ms
       if (not g_spike) and V_m >= Theta:

         /* Set V and Theta to the sodium reversal potential.*/
         V_m = E_Na
         Theta = E_Na

         /* Activate fast potassium current. Drives the*/
         /* membrane potential towards the potassium reversal*/
         /* potential (activate only if duration is non-zero).*/
         if PotassiumRefractoryCounts > 0:
           g_spike = true
         else:
           g_spike = false
         end
         r_potassium = PotassiumRefractoryCounts
         emit_spike()
       end
     end

   function compute_synapse_constant(Tau_1 msTau_2 msg_peak real) real:

       /* Factor used to account for the missing 1/((1/Tau_2)-(1/Tau_1)) term*/
       /* in the ht_neuron_dynamics integration of the synapse terms.*/
       /* See: Exact digital simulation of time-invariant linear systems*/
       /* with applications to neuronal modeling, Rotter and Diesmann,*/
       /* section 3.1.2.*/
       exact_integration_adjustment real = ((1 / Tau_2) - (1 / Tau_1)) * ms
       t_peak real = (Tau_2 * Tau_1) * ln(Tau_2 / Tau_1) / (Tau_2 - Tau_1) / ms
       normalisation_factor real = 1 / (exp(-t_peak / Tau_1) - exp(-t_peak / Tau_2))
       return g_peak * normalisation_factor * exact_integration_adjustment
   end

   end



Characterisation
++++++++++++++++

.. include:: hill_tononi_characterisation.rst


.. footer::

   Generated at 2020-05-27 18:26:45.324410
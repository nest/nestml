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

    
    "r_potassium", "integer", "0", ""    
    "g_spike", "boolean", "false", ""    
    "V_m", "mV", "(g_NaL * E_Na + g_KL * E_K) / (g_NaL + g_KL)", "membrane potential"    
    "Theta", "mV", "Theta_eq", "Threshold"    
    "IKNa_D", "nS", "0.0nS", ""    
    "IT_m", "nS", "0.0nS", ""    
    "IT_h", "nS", "0.0nS", ""    
    "Ih_m", "nS", "0.0nS", ""    
    "g_AMPA", "real", "0", ""    
    "g_NMDA", "real", "0", ""    
    "g_GABAA", "real", "0", ""    
    "g_GABAB", "real", "0", ""    
    "g_AMPA$", "real", "AMPAInitialValue", ""    
    "g_NMDA$", "real", "NMDAInitialValue", ""    
    "g_GABAA$", "real", "GABA_AInitialValue", ""    
    "g_GABAB$", "real", "GABA_BInitialValue", ""




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { \mathrm{nF} } \left( { (\frac 1 { \Tau_{m} } \left( { (I_{Na} + I_{K} + I_{syn} + I_{NaP} + I_{KNa} + I_{T} + I_{h} + I_{e} + I_{stim}) } \right)  + \frac{ I_{spike} \cdot \mathrm{pA} } { (\mathrm{ms} \cdot \mathrm{mV}) }) \cdot \mathrm{s} } \right) 

.. math::
   \frac{ d\Theta } { dt }= \frac{ -(\Theta - \Theta_{eq}) } { \Tau_{\theta} }

.. math::
   \frac{ dIKNa_{D} } { dt }= \frac 1 { \mathrm{ms} } \left( { (D_{influx,peak} \cdot D_{influx} \cdot \mathrm{nS} - \frac 1 { \tau_{D} } \left( { (IKNa_{D} - \frac{ KNa_{D,EQ} } { \mathrm{mV} }) } \right) ) } \right) 

.. math::
   \frac{ dIT_{m} } { dt }= \frac 1 { \mathrm{ms} } \left( { \frac 1 { \tau_{m,T} } \left( { (m_{\infty,T} \cdot \mathrm{nS} - IT_{m}) } \right)  } \right) 

.. math::
   \frac{ dIT_{h} } { dt }= \frac 1 { \mathrm{ms} } \left( { \frac 1 { \tau_{h,T} } \left( { (h_{\infty,T} \cdot \mathrm{nS} - IT_{h}) } \right)  } \right) 

.. math::
   \frac{ dIh_{m} } { dt }= \frac 1 { \mathrm{ms} } \left( { \frac 1 { \tau_{m,h} } \left( { (m_{\infty,h} \cdot \mathrm{nS} - Ih_{m}) } \right)  } \right) 



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `hill_tononi <https://github.com/nest/nestml/tree/master/models/neurons/hill_tononi.nestml>`_.

Characterisation
++++++++++++++++

.. include:: hill_tononi_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.380314
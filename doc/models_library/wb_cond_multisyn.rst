wb_cond_multisyn
################


wb_cond_multisyn - Wang-Buzsaki model with multiple synapses

Description
+++++++++++

wb_cond_multisyn is an implementation of a modified Hodkin-Huxley model.

Spike detection is done by a combined threshold-and-local-maximum search: if
there is a local maximum above a certain threshold of the membrane potential,
it is considered a spike.

AMPA, NMDA, GABA_A, and GABA_B conductance-based synapses with
beta-function (difference of two exponentials) time course.

References
++++++++++

.. [1] Wang, X.J. and Buzsaki, G., (1996) Gamma oscillation by synaptic
       inhibition in a hippocampal interneuronal network model. Journal of
       Neuroscience, 16(20), pp.6402-6413.

See also
++++++++

wb_cond_multisyn



Parameters
++++++++++
.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "t_ref", "ms", "2.0ms", "Refractory period 2.0"    
    "g_Na", "nS", "3500.0nS", "Sodium peak conductance"    
    "g_K", "nS", "900.0nS", "Potassium peak conductance"    
    "g_L", "nS", "10nS", "Leak conductance"    
    "C_m", "pF", "100.0pF", "Membrane Capacitance"    
    "E_Na", "mV", "55.0mV", "Sodium reversal potential"    
    "E_K", "mV", "-90.0mV", "Potassium reversal potentia"    
    "E_L", "mV", "-65.0mV", "Leak reversal Potential (aka resting potential)"    
    "V_Tr", "mV", "-55.0mV", "Spike Threshold"    
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
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "number of steps in the current refractory phase"    
    "V_m", "mV", "-65.0mV", "Membrane potential"    
    "Inact_h", "real", "alpha_h_init / (alpha_h_init + beta_h_init)", "Inactivation variable h for Na"    
    "Act_n", "real", "alpha_n_init / (alpha_n_init + beta_n_init)", "Activation variable n for K"    
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
   \frac{ dInact_{h} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\text{alpha_h}(V_{m}) \cdot (1 - Inact_{h}) - \text{beta_h}(V_{m}) \cdot Inact_{h}) } \right) 

.. math::
   \frac{ dAct_{n} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\text{alpha_n}(V_{m}) \cdot (1 - Act_{n}) - \text{beta_n}(V_{m}) \cdot Act_{n}) } \right) 

.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-(I_{Na} + I_{K} + I_{L}) + I_{e} + I_{stim} + I_{syn}) } \right) 



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `wb_cond_multisyn <https://github.com/nest/nestml/tree/master/models/neurons/wb_cond_multisyn.nestml>`_.

Characterisation
++++++++++++++++

.. include:: wb_cond_multisyn_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.473067
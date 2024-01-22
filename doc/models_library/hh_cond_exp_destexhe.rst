hh_cond_exp_destexhe
####################


hh_cond_exp_destexhe - Hodgin Huxley based model, Traub, Destexhe and Mainen modified

Description
+++++++++++

hh_cond_exp_destexhe is an implementation of a modified Hodkin-Huxley model, which is based on the hh_cond_exp_traub model.

Differences to hh_cond_exp_traub:

(1) **Additional background noise:** A background current whose conductances were modeled as an Ornstein-Uhlenbeck process is injected into the neuron.
(2) **Additional non-inactivating K+ current:** A non-inactivating K+ current was included, which is responsible for spike frequency adaptation.


References
++++++++++

.. [1] Traub, R.D. and Miles, R. (1991) Neuronal Networks of the Hippocampus. Cambridge University Press, Cambridge UK.

.. [2] Destexhe, A. and Pare, D. (1999) Impact of Network Activity on the Integrative Properties of Neocortical Pyramidal Neurons In Vivo. Journal of Neurophysiology

.. [3] A. Destexhe, M. Rudolph, J.-M. Fellous and T. J. Sejnowski (2001) Fluctuating synaptic conductances recreate in vivo-like activity in neocortical neurons. Neuroscience

.. [4] Z. Mainen, J. Joerges, J. R. Huguenard and T. J. Sejnowski (1995) A Model of Spike Initiation in Neocortical Pyramidal Neurons. Neuron


See also
++++++++

hh_cond_exp_traub



Parameters
++++++++++
.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "g_Na", "nS", "17318.0nS", "Na Conductance"    
    "g_K", "nS", "3463.6nS", "K Conductance"    
    "g_L", "nS", "15.5862nS", "Leak Conductance"    
    "C_m", "pF", "346.36pF", "Membrane Capacitance"    
    "E_Na", "mV", "60mV", "Reversal potentials"    
    "E_K", "mV", "-90.0mV", "Potassium reversal potential"    
    "E_L", "mV", "-80.0mV", "Leak reversal Potential (aka resting potential)"    
    "V_T", "mV", "-58.0mV", "Voltage offset that controls dynamics. For default"    
    "tau_syn_exc", "ms", "2.7ms", "parameters, V_T = -63mV results in a threshold around -50mV.Synaptic Time Constant Excitatory Synapse"    
    "tau_syn_inh", "ms", "10.5ms", "Synaptic Time Constant for Inhibitory Synapse"    
    "E_exc", "mV", "0.0mV", "Excitatory synaptic reversal potential"    
    "E_inh", "mV", "-75.0mV", "Inhibitory synaptic reversal potential"    
    "g_M", "nS", "173.18nS", "Conductance of non-inactivating K+ channel"    
    "g_noise_exc0", "uS", "0.012uS", "Conductance OU noiseMean of the excitatory noise conductance"    
    "g_noise_inh0", "uS", "0.057uS", "Mean of the inhibitory noise conductance"    
    "sigma_noise_exc", "uS", "0.003uS", "Standard deviation of the excitatory noise conductance"    
    "sigma_noise_inh", "uS", "0.0066uS", "Standard deviation of the inhibitory noise conductance"    
    "alpha_n_init", "1 / ms", "0.032 / (ms * mV) * (15.0mV - V_m) / (exp((15.0mV - V_m) / 5.0mV) - 1.0)", ""    
    "beta_n_init", "1 / ms", "0.5 / ms * exp((10.0mV - V_m) / 40.0mV)", ""    
    "alpha_m_init", "1 / ms", "0.32 / (ms * mV) * (13.0mV - V_m) / (exp((13.0mV - V_m) / 4.0mV) - 1.0)", ""    
    "beta_m_init", "1 / ms", "0.28 / (ms * mV) * (V_m - 40.0mV) / (exp((V_m - 40.0mV) / 5.0mV) - 1.0)", ""    
    "alpha_h_init", "1 / ms", "0.128 / ms * exp((17.0mV - V_m) / 18.0mV)", ""    
    "beta_h_init", "1 / ms", "(4.0 / (1.0 + exp((40.0mV - V_m) / 5.0mV))) / ms", ""    
    "alpha_p_init", "1 / ms", "0.0001 / (ms * mV) * (V_m + 30.0mV) / (1.0 - exp(-(V_m + 30.0mV) / 9.0mV))", ""    
    "beta_p_init", "1 / ms", "-0.0001 / (ms * mV) * (V_m + 30.0mV) / (1.0 - exp((V_m + 30.0mV) / 9.0mV))", ""    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "counts number of tick during the refractory period"    
    "g_noise_exc", "uS", "g_noise_exc0", ""    
    "g_noise_inh", "uS", "g_noise_inh0", ""    
    "V_m", "mV", "E_L", "Membrane potential"    
    "Act_m", "real", "alpha_m_init / (alpha_m_init + beta_m_init)", ""    
    "Act_h", "real", "alpha_h_init / (alpha_h_init + beta_h_init)", ""    
    "Inact_n", "real", "alpha_n_init / (alpha_n_init + beta_n_init)", ""    
    "Noninact_p", "real", "alpha_p_init / (alpha_p_init + beta_p_init)", ""




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-I_{Na} - I_{K} - I_{M} - I_{L} - I_{syn,exc} - I_{syn,inh} + I_{e} + I_{stim} - I_{noise}) } \right) 

.. math::
   \frac{ dAct_{m} } { dt }= (\alpha_{m} - (\alpha_{m} + \beta_{m}) \cdot Act_{m})

.. math::
   \frac{ dAct_{h} } { dt }= (\alpha_{h} - (\alpha_{h} + \beta_{h}) \cdot Act_{h})

.. math::
   \frac{ dInact_{n} } { dt }= (\alpha_{n} - (\alpha_{n} + \beta_{n}) \cdot Inact_{n})

.. math::
   \frac{ dNoninact_{p} } { dt }= (\alpha_{p} - (\alpha_{p} + \beta_{p}) \cdot Noninact_{p})



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `hh_cond_exp_destexhe <https://github.com/nest/nestml/tree/master/models/neurons/hh_cond_exp_destexhe.nestml>`_.

Characterisation
++++++++++++++++

.. include:: hh_cond_exp_destexhe_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.766222
hh_moto_5ht
###########


hh_moto_5ht_nestml - a motor neuron model in HH formalism with 5HT modulation

Description
+++++++++++

hh_moto_5ht is an implementation of a spiking motor neuron using the Hodgkin-Huxley formalism according to [2]_. Basically this model is an implementation of the existing NEURON model [1]_.

The parameter that represents 5HT modulation is ``g_K_Ca_5ht``. When it equals 1, no modulation happens. An application of 5HT corresponds to its decrease. The default value for it is 0.6. This value was used in the Neuron simulator model. The range of this parameter is (0, 1] but you are free to play with any value.

Post-synaptic currents and spike detection are the same as in hh_psc_alpha.


References
++++++++++

.. [1] Muscle spindle feedback circuit by Moraud EM and Capogrosso M.
       https://senselab.med.yale.edu/ModelDB/showmodel.cshtml?model=189786

.. [2] Compartmental model of vertebrate motoneurons for Ca2+-dependent spiking and plateau potentials under pharmacological treatment.
       Booth V, Rinzel J, Kiehn O.
       http://refhub.elsevier.com/S0896-6273(16)00010-6/sref4

.. [3] Repository: https://github.com/research-team/hh-moto-5ht


See also
++++++++

hh_psc_alpha



Parameters
++++++++++
.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "t_ref", "ms", "2.0ms", "Refractory period"    
    "g_Na", "nS", "5000.0nS", "Sodium peak conductance"    
    "g_L", "nS", "200.0nS", "Leak conductance"    
    "g_K_rect", "nS", "30000.0nS", "Delayed Rectifier Potassium peak conductance"    
    "g_Ca_N", "nS", "5000.0nS", ""    
    "g_Ca_L", "nS", "10.0nS", ""    
    "g_K_Ca", "nS", "30000.0nS", ""    
    "g_K_Ca_5ht", "real", "0.6", "modulation of K-Ca channels by 5HT. Its value 1.0 == no modulation."    
    "Ca_in_init", "mmol", "0.0001mmol", "Initial inside Calcium concentration"    
    "Ca_out", "mmol", "2.0mmol", "Outside Calcium concentration. Remains constant during simulation."    
    "C_m", "pF", "200.0pF", "Membrane capacitance"    
    "E_Na", "mV", "50.0mV", ""    
    "E_K", "mV", "-80.0mV", ""    
    "E_L", "mV", "-70.0mV", ""    
    "R_const", "real", "8.314472", "Nernst equation constants"    
    "F_const", "real", "96485.34", ""    
    "T_current", "real", "309.15", "36 Celcius"    
    "tau_syn_ex", "ms", "0.2ms", "Rise time of the excitatory synaptic alpha function"    
    "tau_syn_in", "ms", "2.0ms", "Rise time of the inhibitory synaptic alpha function"    
    "I_e", "pA", "0pA", "Constant current"    
    "V_m_init", "mV", "-65.0mV", ""    
    "hc_tau", "ms", "50.0ms", ""    
    "mc_tau", "ms", "15.0ms", ""    
    "p_tau", "ms", "400.0ms", ""    
    "alpha", "mmol / pA", "1e-05mmol / pA", ""



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "number of steps in the current refractory phase"    
    "V_m", "mV", "V_m_init", "Membrane potential"    
    "Ca_in", "mmol", "Ca_in_init", "Inside Calcium concentration"    
    "Act_m", "real", "alpha_m(V_m_init) / (alpha_m(V_m_init) + beta_m(V_m_init))", ""    
    "Act_h", "real", "h_inf(V_m_init)", ""    
    "Inact_n", "real", "n_inf(V_m_init)", ""    
    "Act_p", "real", "p_inf(V_m_init)", ""    
    "Act_mc", "real", "mc_inf(V_m_init)", ""    
    "Act_hc", "real", "hc_inf(V_m_init)", ""




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-(I_{Na} + I_{K} + I_{L} + I_{Ca,N} + I_{Ca,L} + I_{K,Ca}) + I_{stim} + I_{e} + I_{syn,inh} + I_{syn,exc}) } \right) 

.. math::
   \frac{ dInact_{n} } { dt }= \frac{ (\text{n_inf}(V_{m}) - Inact_{n}) } { \text{n_tau}(V_{m}) }

.. math::
   \frac{ dAct_{m} } { dt }= \text{alpha_m}(V_{m}) \cdot (1.0 - Act_{m}) - \text{beta_m}(V_{m}) \cdot Act_{m}

.. math::
   \frac{ dAct_{h} } { dt }= \frac{ (\text{h_inf}(V_{m}) - Act_{h}) } { \text{h_tau}(V_{m}) }

.. math::
   \frac{ dAct_{p} } { dt }= \frac 1 { p_{\tau} } \left( { (\text{p_inf}(V_{m}) - Act_{p}) } \right) 

.. math::
   \frac{ dAct_{mc} } { dt }= \frac 1 { mc_{\tau} } \left( { (\text{mc_inf}(V_{m}) - Act_{mc}) } \right) 

.. math::
   \frac{ dAct_{hc} } { dt }= \frac 1 { hc_{\tau} } \left( { (\text{hc_inf}(V_{m}) - Act_{hc}) } \right) 

.. math::
   \frac{ dCa_{in} } { dt }= (\frac{ 0.01 } { \mathrm{s} }) \cdot (-\alpha \cdot (I_{Ca,N} + I_{Ca,L}) - 4.0 \cdot Ca_{in})



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `hh_moto_5ht <https://github.com/nest/nestml/tree/master/models/neurons/hh_moto_5ht.nestml>`_.

Characterisation
++++++++++++++++

.. include:: hh_moto_5ht_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.636925
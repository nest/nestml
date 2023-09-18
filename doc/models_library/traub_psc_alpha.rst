traub_psc_alpha
###############


traub_psc_alpha - Traub model according to Borgers 2017

Reduced Traub-Miles Model of a Pyramidal Neuron in Rat Hippocampus [1]_.
parameters got from reference [2]_.

Incoming spike events induce a post-synaptic change of current modelled
by an alpha function.

References
++++++++++

.. [1] R. D. Traub and R. Miles, Neuronal Networks of the Hippocampus,Cam- bridge University Press, Cambridge, UK, 1991.
.. [2] Borgers, C., 2017. An introduction to modeling neuronal dynamics (Vol. 66). Cham: Springer.


See also
++++++++

hh_cond_exp_traub



Parameters
++++++++++
.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "t_ref", "ms", "2ms", "Refractory period"    
    "g_Na", "nS", "10000nS", "Sodium peak conductance"    
    "g_K", "nS", "8000nS", "Potassium peak conductance"    
    "g_L", "nS", "10nS", "Leak conductance"    
    "C_m", "pF", "100pF", "Membrane capacitance"    
    "E_Na", "mV", "50mV", "Sodium reversal potential"    
    "E_K", "mV", "-100mV", "Potassium reversal potential"    
    "E_L", "mV", "-67mV", "Leak reversal potential (aka resting potential)"    
    "V_Tr", "mV", "-20mV", "Spike threshold"    
    "tau_syn_exc", "ms", "0.2ms", "Rise time of the excitatory synaptic alpha function"    
    "tau_syn_inh", "ms", "2ms", "Rise time of the inhibitory synaptic alpha function"    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "number of steps in the current refractory phase"    
    "V_m", "mV", "-70.0mV", "Membrane potential"    
    "Act_m", "real", "alpha_m_init / (alpha_m_init + beta_m_init)", "Activation variable m for Na"    
    "Inact_h", "real", "alpha_h_init / (alpha_h_init + beta_h_init)", "Inactivation variable h for Na"    
    "Act_n", "real", "alpha_n_init / (alpha_n_init + beta_n_init)", "Activation variable n for K"




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-(I_{Na} + I_{K} + I_{L}) + I_{e} + I_{stim} + I_{syn,exc} - I_{syn,inh}) } \right) 

.. math::
   \frac{ dAct_{n} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{n} \cdot (1 - Act_{n}) - \beta_{n} \cdot Act_{n}) } \right) 

.. math::
   \frac{ dAct_{m} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{m} \cdot (1 - Act_{m}) - \beta_{m} \cdot Act_{m}) } \right) 

.. math::
   \frac{ dInact_{h} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{h} \cdot (1 - Inact_{h}) - \beta_{h} \cdot Inact_{h}) } \right) 



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `traub_psc_alpha <https://github.com/nest/nestml/tree/master/models/neurons/traub_psc_alpha.nestml>`_.

Characterisation
++++++++++++++++

.. include:: traub_psc_alpha_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.304255
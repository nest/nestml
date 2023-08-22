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

The model source code can be found in the NESTML models repository here: `terub_gpe <https://github.com/nest/nestml/tree/master/models/neurons/terub_gpe.nestml>`_.

Characterisation
++++++++++++++++

.. include:: terub_gpe_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.246054
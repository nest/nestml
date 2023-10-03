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



Parameters
++++++++++
.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "E_L", "mV", "-60mV", "Resting membrane potential"    
    "g_L", "nS", "2.25nS", "Leak conductance"    
    "C_m", "pF", "1pF", "Capacity of the membrane"    
    "E_Na", "mV", "55mV", "Sodium reversal potential"    
    "g_Na", "nS", "37.5nS", "Sodium peak conductance"    
    "E_K", "mV", "-80mV", "Potassium reversal potential"    
    "g_K", "nS", "45nS", "Potassium peak conductance"    
    "E_Ca", "mV", "140mV", "Calcium reversal potential"    
    "g_Ca", "nS", "0.5nS", "Calcium peak conductance"    
    "g_T", "nS", "0.5nS", "T-type Calcium channel peak conductance"    
    "g_ahp", "nS", "9nS", "Afterpolarization current peak conductance"    
    "tau_syn_exc", "ms", "1ms", "Rise time of the excitatory synaptic alpha function"    
    "tau_syn_inh", "ms", "0.08ms", "Rise time of the inhibitory synaptic alpha function"    
    "E_gs", "mV", "-85mV", "Reversal potential for inhibitory input (from GPe)"    
    "t_ref", "ms", "2ms", "Refractory time"    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "counts number of tick during the refractory period"    
    "V_m", "mV", "E_L", "Membrane potential"    
    "gate_h", "real", "0.0", "gating variable h"    
    "gate_n", "real", "0.0", "gating variable n"    
    "gate_r", "real", "0.0", "gating variable r"    
    "Ca_con", "real", "0.0", "gating variable r"




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-(I_{Na} + I_{K} + I_{L} + I_{T} + I_{Ca} + I_{ahp}) + I_{e} + I_{stim} + I_{exc,mod} + I_{inh,mod}) } \right) 

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

The model source code can be found in the NESTML models repository here: `terub_stn <https://github.com/nest/nestml/tree/master/models/neurons/terub_stn.nestml>`_.

Characterisation
++++++++++++++++

.. include:: terub_stn_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.333524
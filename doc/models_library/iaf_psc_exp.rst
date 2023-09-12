iaf_psc_exp
###########


iaf_psc_exp - Leaky integrate-and-fire neuron model with exponential PSCs

Description
+++++++++++

iaf_psc_exp is an implementation of a leaky integrate-and-fire model
with exponential-kernel postsynaptic currents (PSCs) according to [1]_.
Thus, postsynaptic currents have an infinitely short rise time.

The threshold crossing is followed by an absolute refractory period (t_ref)
during which the membrane potential is clamped to the resting potential
and spiking is prohibited.

.. note::
   If tau_m is very close to tau_syn_exc or tau_syn_inh, numerical problems
   may arise due to singularities in the propagator matrics. If this is
   the case, replace equal-valued parameters by a single parameter.

   For details, please see ``IAF_neurons_singularity.ipynb`` in
   the NEST source code (``docs/model_details``).


References
++++++++++

.. [1] Tsodyks M, Uziel A, Markram H (2000). Synchrony generation in recurrent
       networks with frequency-dependent synapses. The Journal of Neuroscience,
       20,RC50:1-5. URL: https://infoscience.epfl.ch/record/183402


See also
++++++++

iaf_cond_exp



Parameters
++++++++++
.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "C_m", "pF", "250pF", "Capacitance of the membrane"    
    "tau_m", "ms", "10ms", "Membrane time constant"    
    "tau_syn_inh", "ms", "2ms", "Time constant of inhibitory synaptic current"    
    "tau_syn_exc", "ms", "2ms", "Time constant of excitatory synaptic current"    
    "t_ref", "ms", "2ms", "Duration of refractory period"    
    "E_L", "mV", "-70mV", "Resting potential"    
    "V_reset", "mV", "-70mV", "Reset value of the membrane potential"    
    "V_th", "mV", "-55mV", "Spike threshold potential"    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "Counts number of tick during the refractory period"    
    "V_m", "mV", "E_L", "Membrane potential"




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac{ -(V_{m} - E_{L}) } { \tau_{m} } + \frac 1 { C_{m} } \left( { (I_{syn} + I_{e} + I_{stim}) } \right) 



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `iaf_psc_exp <https://github.com/nest/nestml/tree/master/models/neurons/iaf_psc_exp.nestml>`_.

Characterisation
++++++++++++++++

.. include:: iaf_psc_exp_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.614878
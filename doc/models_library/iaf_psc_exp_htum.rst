iaf_psc_exp_htum
################


iaf_psc_exp_htum - Leaky integrate-and-fire model with separate relative and absolute refractory period

Description
+++++++++++

iaf_psc_exp_htum is an implementation of a leaky integrate-and-fire model
with exponential-kernel postsynaptic currents (PSCs) according to [1]_.
The postsynaptic currents have an infinitely short rise time.
In particular, this model allows setting an absolute and relative
refractory time separately, as required by [1]_.

The threshold crossing is followed by an absolute refractory period
(t_ref_abs) during which the membrane potential is clamped to the resting
potential. During the total refractory period (t_ref_tot), the membrane
potential evolves, but the neuron will not emit a spike, even if the
membrane potential reaches threshold. The total refractory time must be
larger or equal to the absolute refractory time. If equal, the
refractoriness of the model if equivalent to the other models of NEST.

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
.. [2] Hill, A. V. (1936). Excitation and accommodation in nerve. Proceedings of
       the Royal Society of London. Series B-Biological Sciences, 119(814), 305-355.
       DOI: https://doi.org/10.1098/rspb.1936.0012
.. [3] Rotter S,  Diesmann M (1999). Exact simulation of
       time-invariant linear systems with applications to neuronal
       modeling. Biologial Cybernetics 81:381-402.
       DOI: https://doi.org/10.1007/s004220050570
.. [4] Diesmann M, Gewaltig M-O, Rotter S, & Aertsen A (2001). State
       space analysis of synchronous spiking in cortical neural
       networks. Neurocomputing 38-40:565-571.
       DOI: https://doi.org/10.1016/S0925-2312(01)00409-X



Parameters
++++++++++
.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "C_m", "pF", "250pF", "Capacitance of the membrane"    
    "tau_m", "ms", "10ms", "Membrane time constant"    
    "tau_syn_inh", "ms", "2ms", "Time constant of inhibitory synaptic current"    
    "tau_syn_exc", "ms", "2ms", "Time constant of excitatory synaptic current"    
    "t_ref_abs", "ms", "2ms", "Absolute refractory period"    
    "t_ref_tot", "ms", "2ms", "total refractory period, if t_ref_abs == t_ref_tot iaf_psc_exp_htum equivalent to iaf_psc_exp"    
    "E_L", "mV", "-70mV", "Resting potential"    
    "V_reset", "mV", "-70.0mV - E_L", "Reset value of the membrane potentia. lRELATIVE TO RESTING POTENTIAL(!) I.e. the real threshold is (V_reset + E_L)."    
    "V_th", "mV", "-55.0mV - E_L", "Threshold, RELATIVE TO RESTING POTENTIAL(!) I.e. the real threshold is (E_L + V_th)"    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r_tot", "integer", "0", ""    
    "r_abs", "integer", "0", ""    
    "V_m", "mV", "0.0mV", "Membrane potential"




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac{ -V_{m} } { \tau_{m} } + \frac 1 { C_{m} } \left( { (I_{syn} + I_{e} + I_{stim}) } \right) 



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `iaf_psc_exp_htum <https://github.com/nest/nestml/tree/master/models/neurons/iaf_psc_exp_htum.nestml>`_.

Characterisation
++++++++++++++++

.. include:: iaf_psc_exp_htum_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.584571
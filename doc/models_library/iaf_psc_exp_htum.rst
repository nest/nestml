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
   If tau_m is very close to tau_syn_ex or tau_syn_in, numerical problems
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

Author
++++++

Moritz Helias (March 2006)


Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "C_m", "pF", "250pF", "Capacity of the membrane"    
    "tau_m", "ms", "10ms", "Membrane time constant."    
    "tau_syn_in", "ms", "2ms", "Time constant of synaptic current."    
    "tau_syn_ex", "ms", "2ms", "Time constant of synaptic current."    
    "t_ref_abs", "ms", "2ms", "absolute refractory period."    
    "t_ref_tot", "ms", "2ms", "total refractory periodif t_ref_abs == t_ref_tot iaf_psc_exp_htum equivalent to iaf_psc_exp"    
    "E_L", "mV", "-70mV", "Resting potential."    
    "V_reset", "mV", "-70.0mV - E_L", "Reset value of the membrane potential"    
    "V_th", "mV", "-55.0mV - E_L", "RELATIVE TO RESTING POTENTIAL(!).I.e. the real threshold is (V_reset + E_L).Threshold, RELATIVE TO RESTING POTENTIAL(!)."    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "0.0mV", "Membrane potential"




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac{ -V_{m} } { \tau_{m} } + \frac 1 { C_{m} } \left( { (I_{syn} + I_{e} + I_{stim}) } \right) 





Source code
+++++++++++

.. code:: nestml

   neuron iaf_psc_exp_htum:
     state:
       r_tot integer = 0
       r_abs integer = 0
     end
     initial_values:
       V_m mV = 0.0mV # Membrane potential
     end
     equations:
       kernel I_kernel_in = exp(-1 / tau_syn_in * t)
       kernel I_kernel_ex = exp(-1 / tau_syn_ex * t)
       function I_syn pA = convolve(I_kernel_in,in_spikes) + convolve(I_kernel_ex,ex_spikes)
       V_m'=-V_m / tau_m + (I_syn + I_e + I_stim) / C_m
     end

     parameters:
       C_m pF = 250pF # Capacity of the membrane
       tau_m ms = 10ms # Membrane time constant.
       tau_syn_in ms = 2ms # Time constant of synaptic current.
       tau_syn_ex ms = 2ms # Time constant of synaptic current.
       t_ref_abs ms = 2ms # absolute refractory period.
       /* total refractory period*/

       /* total refractory period*/
       t_ref_tot ms = 2ms [[t_ref_tot >= t_ref_abs]] # if t_ref_abs == t_ref_tot iaf_psc_exp_htum equivalent to iaf_psc_exp
       E_L mV = -70mV # Resting potential.
       function V_reset mV = -70.0mV - E_L # Reset value of the membrane potential
       /* RELATIVE TO RESTING POTENTIAL(!).*/
       /* I.e. the real threshold is (V_reset + E_L).*/

       /* RELATIVE TO RESTING POTENTIAL(!).*/
       /* I.e. the real threshold is (V_reset + E_L).*/
       function V_th mV = -55.0mV - E_L # Threshold, RELATIVE TO RESTING POTENTIAL(!).
       /* I.e. the real threshold is (E_L+V_th).*/

       /* constant external input current*/
       I_e pA = 0pA
     end
     internals:

       /* TauR specifies the length of the absolute refractory period as*/
       /* a double_t in ms. The grid based iaf_psc_exp_htum can only handle refractory*/
       /* periods that are integer multiples of the computation step size (h).*/
       /* To ensure consistency with the overall simulation scheme such conversion*/
       /* should be carried out via objects of class nest::Time. The conversion*/
       /* requires 2 steps:*/
       /*     1. A time object r is constructed defining  representation of*/
       /*        TauR in tics. This representation is then converted to computation*/
       /*        time steps again by a strategy defined by class nest::Time.*/
       /*     2. The refractory time in units of steps is read out get_steps(), a*/
       /*        member function of class nest::Time.*/
       /**/
       /* Choosing a TauR that is not an integer multiple of the computation time*/
       /* step h will leed to accurate (up to the resolution h) and self-consistent*/
       /* results. However, a neuron model capable of operating with real valued*/
       /* spike time may exhibit a different effective refractory time.*/
       RefractoryCountsAbs integer = steps(t_ref_abs) [[RefractoryCountsAbs > 0]]
       RefractoryCountsTot integer = steps(t_ref_tot) [[RefractoryCountsTot > 0]]
     end
     input:
       ex_spikes pA <-excitatory spike
       in_spikes pA <-inhibitory spike
       I_stim pA <-current
     end

     output: spike

     update:
       if r_abs == 0: # neuron not absolute refractory, so evolve V
         integrate_odes()
       else:
         r_abs -= 1 # neuron is absolute refractory
       end
       if r_tot == 0:
         if V_m >= V_th: # threshold crossing
           r_abs = RefractoryCountsAbs
           r_tot = RefractoryCountsTot
           V_m = V_reset
           emit_spike()
         end
       else:
         r_tot -= 1 # neuron is totally refractory (cannot generate spikes)
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: iaf_psc_exp_htum_characterisation.rst


.. footer::

   Generated at 2020-05-27 18:26:44.972470

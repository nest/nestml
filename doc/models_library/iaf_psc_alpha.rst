iaf_psc_alpha
#############

iaf_psc_alpha - Leaky integrate-and-fire neuron model


Description
+++++++++++

iaf_psc_alpha is an implementation of a leaky integrate-and-fire model
with alpha-kernel synaptic currents. Thus, synaptic currents and the
resulting post-synaptic potentials have a finite rise time.

The threshold crossing is followed by an absolute refractory period
during which the membrane potential is clamped to the resting potential.

The general framework for the consistent formulation of systems with
neuron like dynamics interacting by point events is described in
[1]_.  A flow chart can be found in [2]_.

Critical tests for the formulation of the neuron model are the
comparisons of simulation results for different computation step
sizes.

The iaf_psc_alpha is the standard model used to check the consistency
of the nest simulation kernel because it is at the same time complex
enough to exhibit non-trivial dynamics and simple enough compute
relevant measures analytically.

.. note::
   If tau_m is very close to tau_syn_ex or tau_syn_in, numerical problems
   may arise due to singularities in the propagator matrics. If this is
   the case, replace equal-valued parameters by a single parameter.

   For details, please see ``IAF_neurons_singularity.ipynb`` in
   the NEST source code (``docs/model_details``).


Parameters
++++++++++

The following parameters can be set in the status dictionary.

=========== ======  ==========================================================
 V_m        mV      Membrane potential
 E_L        mV      Resting membrane potential
 C_m        pF      Capacity of the membrane
 tau_m      ms      Membrane time constant
 t_ref      ms      Duration of refractory period
 V_th       mV      Spike threshold
 V_reset    mV      Reset potential of the membrane
 tau_syn_ex ms      Rise time of the excitatory synaptic alpha function
 tau_syn_in ms      Rise time of the inhibitory synaptic alpha function
 I_e        pA      Constant input current
 V_min      mV      Absolute lower value for the membrane potenial
=========== ======  ==========================================================


References
++++++++++

.. [1] Rotter S,  Diesmann M (1999). Exact simulation of
       time-invariant linear systems with applications to neuronal
       modeling. Biologial Cybernetics 81:381-402.
       DOI: https://doi.org/10.1007/s004220050570
.. [2] Diesmann M, Gewaltig M-O, Rotter S, & Aertsen A (2001). State
       space analysis of synchronous spiking in cortical neural
       networks. Neurocomputing 38-40:565-571.
       DOI: https://doi.org/10.1016/S0925-2312(01)00409-X
.. [3] Morrison A, Straube S, Plesser H E, Diesmann M (2006). Exact
       subthreshold integration with continuous spike times in discrete time
       neural network simulations. Neural Computation, in press
       DOI: https://doi.org/10.1162/neco.2007.19.1.47


See also
++++++++

iaf_psc_delta, iaf_psc_exp, iaf_cond_alpha


Authors
+++++++

Diesmann, Gewaltig


Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "C_m", "pF", "250pF", "Capacity of the membrane"    
    "Tau", "ms", "10ms", "Membrane time constant."    
    "tau_syn_in", "ms", "2ms", "Time constant of synaptic current."    
    "tau_syn_ex", "ms", "2ms", "Time constant of synaptic current."    
    "t_ref", "ms", "2ms", "Duration of refractory period."    
    "E_L", "mV", "-70mV", "Resting potential."    
    "V_reset", "mV", "-70mV - E_L", "Reset potential of the membrane."    
    "Theta", "mV", "-55mV - E_L", "Spike threshold."    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_abs", "mV", "0mV", ""    
    "V_m", "mV", "V_abs + E_L", "Membrane potential."




Equations
+++++++++




.. math::
   \frac{ dV_{abs} } { dt }= \frac{ -1 } { \Tau } \cdot V_{abs} + \frac{ 1 } { C_{m} } \cdot I





Source code
+++++++++++

.. code:: nestml

   neuron iaf_psc_alpha:
     state:
       r integer  # counts number of tick during the refractory period
     end
     initial_values:
       V_abs mV = 0mV
       function V_m mV = V_abs + E_L # Membrane potential.
     end
     equations:
       kernel I_kernel_in = pA * (e / tau_syn_in) * t * exp(-1 / tau_syn_in * t)
       kernel I_kernel_ex = pA * (e / tau_syn_ex) * t * exp(-1 / tau_syn_ex * t)
       function I pA = convolve(I_kernel_in,in_spikes) + convolve(I_kernel_ex,ex_spikes) + I_e + I_stim
       V_abs'=-1 / Tau * V_abs + 1 / C_m * I
     end

     parameters:
       C_m pF = 250pF # Capacity of the membrane
       Tau ms = 10ms # Membrane time constant.
       tau_syn_in ms = 2ms # Time constant of synaptic current.
       tau_syn_ex ms = 2ms # Time constant of synaptic current.
       t_ref ms = 2ms # Duration of refractory period.
       E_L mV = -70mV # Resting potential.
       function V_reset mV = -70mV - E_L # Reset potential of the membrane.
       function Theta mV = -55mV - E_L # Spike threshold.

       /* constant external input current*/
       I_e pA = 0pA
     end
     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end
     input:
       ex_spikes pA <-excitatory spike
       in_spikes pA <-inhibitory spike
       I_stim pA <-current
     end

     output: spike

     update:
       if r == 0: # neuron not refractory
         integrate_odes()
       else:
         r = r - 1
       end
       if V_abs >= Theta: # threshold crossing

         /* A supra-threshold membrane potential should never be observable.*/
         /* The reset at the time of threshold crossing enables accurate*/
         /* integration independent of the computation step size, see [2,3] for*/
         /* details.*/
         r = RefractoryCounts
         V_abs = V_reset
         emit_spike()
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: iaf_psc_alpha_characterisation.rst


.. footer::

   Generated at 2020-05-27 18:26:45.061053

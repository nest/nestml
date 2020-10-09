iaf_psc_delta
#############

iaf_psc_delta - Current-based leaky integrate-and-fire neuron model with delta-kernel post-synaptic currents


Description
+++++++++++

iaf_psc_delta is an implementation of a leaky integrate-and-fire model
where the potential jumps on each spike arrival.

The threshold crossing is followed by an absolute refractory period
during which the membrane potential is clamped to the resting potential.

Spikes arriving while the neuron is refractory, are discarded by
default. If the property ``with_refr_input`` is set to true, such
spikes are added to the membrane potential at the end of the
refractory period, dampened according to the interval between
arrival and end of refractoriness.

The general framework for the consistent formulation of systems with
neuron like dynamics interacting by point events is described in
[1]_.  A flow chart can be found in [2]_.

Critical tests for the formulation of the neuron model are the
comparisons of simulation results for different computation step
sizes. sli/testsuite/nest contains a number of such tests.

The iaf_psc_delta is the standard model used to check the consistency
of the nest simulation kernel because it is at the same time complex
enough to exhibit non-trivial dynamics and simple enough compute
relevant measures analytically.


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


See also
++++++++

iaf_psc_alpha, iaf_psc_exp


Authors
+++++++

Diesmann, Gewaltig (September 1999)


Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "tau_m", "ms", "10ms", "Membrane time constant."    
    "C_m", "pF", "250pF", "Capacity of the membrane"    
    "t_ref", "ms", "2ms", "Duration of refractory period."    
    "tau_syn", "ms", "2ms", "Time constant of synaptic current."    
    "E_L", "mV", "-70mV", "Resting membrane potential."    
    "V_reset", "mV", "-70mV - E_L", "Reset potential of the membrane."    
    "Theta", "mV", "-55mV - E_L", "Spike threshold."    
    "V_min", "mV", "-inf * 1mV", "Absolute lower value for the membrane potential"    
    "with_refr_input", "boolean", "false", "If true, do not discard input during  refractory period. Default: false."    
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
   \frac{ dV_{abs} } { dt }= \frac{ -1 } { \tau_{m} } \cdot V_{abs} + \frac{ 1 } { C_{m} } \cdot (\text{convolve}(G, spikes) + I_{e} + I_{stim})





Source code
+++++++++++

.. code:: nestml

   neuron iaf_psc_delta:
     state:
       refr_spikes_buffer mV = 0mV
       r integer  # counts number of tick during the refractory period
     end
     initial_values:
       V_abs mV = 0mV
       function V_m mV = V_abs + E_L # Membrane potential.
     end
     equations:
       kernel G = delta(t,tau_m)
       V_abs'=-1 / tau_m * V_abs + 1 / C_m * (convolve(G,spikes) + I_e + I_stim)
     end

     parameters:
       tau_m ms = 10ms # Membrane time constant.
       C_m pF = 250pF # Capacity of the membrane
       t_ref ms = 2ms # Duration of refractory period.
       tau_syn ms = 2ms # Time constant of synaptic current.
       E_L mV = -70mV # Resting membrane potential.
       function V_reset mV = -70mV - E_L # Reset potential of the membrane.
       function Theta mV = -55mV - E_L # Spike threshold.
       V_min mV = -inf * 1mV # Absolute lower value for the membrane potential
       with_refr_input boolean = false # If true, do not discard input during  refractory period. Default: false.

       /* constant external input current*/
       I_e pA = 0pA
     end
     internals:
       h ms = resolution()
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end
     input:
       spikes pA <-spike
       I_stim pA <-current
     end

     output: spike

     update:
       if r == 0: # neuron not refractory
         integrate_odes()

         /* if we have accumulated spikes from refractory period,*/
         /* add and reset accumulator*/
         if with_refr_input and refr_spikes_buffer != 0.0mV:
           V_abs += refr_spikes_buffer
           refr_spikes_buffer = 0.0mV
         end

         /* lower bound of membrane potential*/
         V_abs = V_abs < V_min?V_min:V_abs
       else:

         /* read spikes from buffer and accumulate them, discounting*/
         /* for decay until end of refractory period*/
         /* the buffer is clear automatically*/
         if with_refr_input:
           refr_spikes_buffer += spikes * exp(-r * h / tau_m) * mV / pA
         end
         r -= 1
       end
       if V_abs >= Theta: # threshold crossing
         r = RefractoryCounts
         V_abs = V_reset
         emit_spike()
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: iaf_psc_delta_characterisation.rst


.. footer::

   Generated at 2020-05-27 18:26:45.171065

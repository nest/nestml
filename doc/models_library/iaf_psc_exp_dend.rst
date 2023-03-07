iaf_psc_exp_dend
################


iaf_psc_exp_dend - Leaky integrate-and-fire neuron model with exponential PSCs

Description
+++++++++++

iaf_psc_exp is an implementation of a leaky integrate-and-fire model
with exponential-kernel postsynaptic currents (PSCs) according to [1]_.
Thus, postsynaptic currents have an infinitely short rise time.

The threshold crossing is followed by an absolute refractory period (t_ref)
during which the membrane potential is clamped to the resting potential
and spiking is prohibited.

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


See also
++++++++

iaf_cond_exp



Parameters
++++++++++
  Capacity of the membrane.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "C_m", "pF", "250pF", "Capacity of the membrane"    
    "tau_m", "ms", "10ms", "Membrane time constant"    
    "tau_syn_inh", "ms", "2ms", "Time constant of inhibitory synaptic current"    
    "tau_syn_exc", "ms", "2ms", "Time constant of excitatory synaptic current"    
    "t_ref", "ms", "2ms", "Duration of refractory period"    
    "E_L", "mV", "-70mV", "Resting potential"    
    "V_reset", "mV", "-70mV", "Reset potential of the membrane"    
    "V_th", "mV", "-55mV", "Spike threshold potential"    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "Counts number of ticks during the refractory period"    
    "V_m", "mV", "E_L", "Membrane potential"    
    "I_dend", "pA", "0pA", "Third factor, to be read out by synapse during weight update"




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac{ -(V_{m} - E_{L}) } { \tau_{m} } + \frac 1 { C_{m} } \left( { (I_{syn} + I_{e} + I_{stim}) } \right) 



Source code
+++++++++++

.. code-block:: nestml

   neuron iaf_psc_exp_dend:
       state: # Counts number of ticks during the refractory period
           r integer = 0 # Counts number of ticks during the refractory period
           V_m mV = E_L # Membrane potential
           I_dend pA = 0pA # Third factor, to be read out by synapse during weight update
       equations:
           kernel I_kernel_inh = exp(-t / tau_syn_inh)
           kernel I_kernel_exc = exp(-t / tau_syn_exc)
           inline I_syn pA = convolve(I_kernel_exc,exc_spikes) - convolve(I_kernel_inh,inh_spikes)
           V_m' = -(V_m - E_L) / tau_m + (I_syn + I_e + I_stim) / C_m
       parameters: # Capacity of the membrane
           C_m pF = 250pF # Capacity of the membrane
           tau_m ms = 10ms # Membrane time constant
           tau_syn_inh ms = 2ms # Time constant of inhibitory synaptic current
           tau_syn_exc ms = 2ms # Time constant of excitatory synaptic current
           t_ref ms = 2ms # Duration of refractory period
           E_L mV = -70mV # Resting potential
           V_reset mV = -70mV # Reset potential of the membrane
           V_th mV = -55mV # Spike threshold potential
           # constant external input current
           I_e pA = 0pA
       internals: # refractory time in steps
           RefractoryCounts integer = steps(t_ref) # refractory time in steps
       input:
           exc_spikes pA <-excitatory spike
           inh_spikes pA <-inhibitory spike
           I_stim pA <-current
       output: spike
       update:
           I_dend *= 0.95
           if r == 0: # neuron not refractory, so evolve V
               integrate_odes() # neuron is absolute refractory
           else:
               r = r - 1 # neuron is absolute refractory
        
           if V_m >= V_th: # threshold crossing
               r = RefractoryCounts
               V_m = V_reset
               emit_spike()
        



Characterisation
++++++++++++++++

.. include:: iaf_psc_exp_dend_characterisation.rst


.. footer::

   Generated at 2023-03-09 09:13:57.116865
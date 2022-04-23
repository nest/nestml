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



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "C_m", "pF", "250pF", "Capacity of the membrane"    
    "tau_m", "ms", "10ms", "Membrane time constant"    
    "tau_syn_inh", "ms", "2ms", "Time constant of inhibitory synaptic current"    
    "tau_syn_exc", "ms", "2ms", "Time constant of excitatory synaptic current"    
    "t_ref", "ms", "2ms", "Duration of refractory period"    
    "E_L", "mV", "-70mV", "Resting potential"    
    "V_reset", "mV", "-70mV - E_L", "reset value of the membrane potential"    
    "Theta", "mV", "-55mV - E_L", "Threshold, RELATIVE TO RESTING POTENTIAL (!)."    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "counts number of tick during the refractory period"    
    "V_abs", "mV", "0mV", ""    
    "I_dend", "pA", "0pA", "third factor, to be read out by synapse during weight update"




Equations
+++++++++




.. math::
   \frac{ dV_{abs} } { dt }= \frac{ -V_{abs} } { \tau_{m} } + \frac 1 { C_{m} } \left( { (I_{syn} + I_{e} + I_{stim}) } \right) 





Source code
+++++++++++

.. code-block:: nestml

   neuron iaf_psc_exp_dend:
     state:
       r integer = 0 # counts number of tick during the refractory period
       V_abs mV = 0mV
       I_dend pA = 0pA # third factor, to be read out by synapse during weight update
     end
     equations:
       kernel I_kernel_inh = exp(-t / tau_syn_inh)
       kernel I_kernel_exc = exp(-t / tau_syn_exc)
   recordable    inline V_m mV = V_abs + E_L # Membrane potential.
       inline I_syn pA = convolve(I_kernel_exc,exc_spikes) - convolve(I_kernel_inh,inh_spikes)
       V_abs'=-V_abs / tau_m + (I_syn + I_e + I_stim) / C_m
     end

     parameters:
       C_m pF = 250pF # Capacity of the membrane
       tau_m ms = 10ms # Membrane time constant
       tau_syn_inh ms = 2ms # Time constant of inhibitory synaptic current
       tau_syn_exc ms = 2ms # Time constant of excitatory synaptic current
       t_ref ms = 2ms # Duration of refractory period
       E_L mV = -70mV # Resting potential
       V_reset mV = -70mV - E_L # reset value of the membrane potential
       Theta mV = -55mV - E_L # Threshold, RELATIVE TO RESTING POTENTIAL (!).
       # I.e. the real threshold is (E_L_+V_th_)

       # constant external input current
       I_e pA = 0pA
     end
     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end
     input:
       exc_spikes pA <-excitatory spike
       inh_spikes pA <-inhibitory spike
       I_stim pA <-current
     end

     output: spike

     update:
       I_dend *= 0.95
       if r == 0: # neuron not refractory, so evolve V
         integrate_odes()
       else:
         r = r - 1 # neuron is absolute refractory
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

.. include:: iaf_psc_exp_dend_characterisation.rst


.. footer::

   Generated at 2022-03-28 19:04:29.801538
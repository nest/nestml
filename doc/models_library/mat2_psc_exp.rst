mat2_psc_exp
############

mat2_psc_exp - Non-resetting leaky integrate-and-fire neuron model with exponential PSCs and adaptive threshold


Description
+++++++++++

mat2_psc_exp is an implementation of a leaky integrate-and-fire model
with exponential-kernel postsynaptic currents (PSCs). Thus, postsynaptic
currents have an infinitely short rise time.

The threshold is lifted when the neuron is fired and then decreases in a
fixed time scale toward a fixed level [3]_.

The threshold crossing is followed by a total refractory period
during which the neuron is not allowed to fire, even if the membrane
potential exceeds the threshold. The membrane potential is NOT reset,
but continuously integrated.

.. note::
   If tau_m is very close to tau_syn_ex or tau_syn_in, numerical problems
   may arise due to singularities in the propagator matrics. If this is
   the case, replace equal-valued parameters by a single parameter.

   For details, please see ``IAF_neurons_singularity.ipynb`` in
   the NEST source code (``docs/model_details``).


References
++++++++++

.. [1] Rotter S and Diesmann M (1999). Exact simulation of
       time-invariant linear systems with applications to neuronal
       modeling. Biologial Cybernetics 81:381-402.
       DOI: https://doi.org/10.1007/s004220050570
.. [2] Diesmann M, Gewaltig M-O, Rotter S, Aertsen A (2001). State
       space analysis of synchronous spiking in cortical neural
       networks. Neurocomputing 38-40:565-571.
       DOI:https://doi.org/10.1016/S0925-2312(01)00409-X
.. [3] Kobayashi R, Tsubo Y and Shinomoto S (2009). Made-to-order
       spiking neuron model equipped with a multi-timescale adaptive
       threshold. Frontiers in Computuational Neuroscience 3:9.
       DOI: https://doi.org/10.3389/neuro.10.009.2009

Author
++++++

Thomas Pfeil (modified iaf_psc_exp model of Moritz Helias)


Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "tau_m", "ms", "5ms", "Membrane time constant"    
    "C_m", "pF", "100pF", "Capacity of the membrane"    
    "t_ref", "ms", "2ms", "Duration of absolute refractory period (no spiking)"    
    "E_L", "mV", "-70.0mV", "Resting potential"    
    "tau_syn_ex", "ms", "1ms", "Time constant of postsynaptic excitatory currents"    
    "tau_syn_in", "ms", "3ms", "Time constant of postsynaptic inhibitory currents"    
    "tau_1", "ms", "10ms", "Short time constant of adaptive threshold"    
    "tau_2", "ms", "200ms", "Long time constant of adaptive threshold"    
    "alpha_1", "mV", "37.0mV", "Amplitude of short time threshold adaption [3]"    
    "alpha_2", "mV", "2.0mV", "Amplitude of long time threshold adaption [3]"    
    "omega", "mV", "19.0mV", "Resting spike threshold (absolute value, not relative to E_L)"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_abs", "mV", "0mV", "Membrane potential"    
    "V_m", "mV", "V_abs + E_L", "Relative membrane potential."




Equations
+++++++++




.. math::
   \frac{ dV_{abs} } { dt }= \frac{ -V_{abs} } { \tau_{m} } + \frac 1 { C_{m} } \left( { (I_{syn} + I_{e} + I_{stim}) } \right) 





Source code
+++++++++++

.. code:: nestml

   neuron mat2_psc_exp:
     state:
       V_th_alpha_1 mV  # Two-timescale adaptive threshold
       V_th_alpha_2 mV  # Two-timescale adaptive threshold
       r integer  # counts number of tick during the refractory period
     end
     initial_values:
       V_abs mV = 0mV # Membrane potential
       function V_m mV = V_abs + E_L # Relative membrane potential.
       /* I.e. the real threshold is (V_m-E_L).*/

     end
     equations:
       kernel I_kernel_in = exp(-1 / tau_syn_in * t)
       kernel I_kernel_ex = exp(-1 / tau_syn_ex * t)

       /* V_th_alpha_1' = -V_th_alpha_1/tau_1*/
       /* V_th_alpha_2' = -V_th_alpha_2/tau_2*/
       function I_syn pA = convolve(I_kernel_in,in_spikes) + convolve(I_kernel_ex,ex_spikes)
       V_abs'=-V_abs / tau_m + (I_syn + I_e + I_stim) / C_m
     end

     parameters:
       tau_m ms = 5ms # Membrane time constant
       C_m pF = 100pF # Capacity of the membrane
       t_ref ms = 2ms # Duration of absolute refractory period (no spiking)
       E_L mV = -70.0mV # Resting potential
       tau_syn_ex ms = 1ms # Time constant of postsynaptic excitatory currents
       tau_syn_in ms = 3ms # Time constant of postsynaptic inhibitory currents
       tau_1 ms = 10ms # Short time constant of adaptive threshold
       tau_2 ms = 200ms # Long time constant of adaptive threshold
       alpha_1 mV = 37.0mV # Amplitude of short time threshold adaption [3]
       alpha_2 mV = 2.0mV # Amplitude of long time threshold adaption [3]
       omega mV = 19.0mV # Resting spike threshold (absolute value, not relative to E_L)

       /* constant external input current*/
       I_e pA = 0pA
     end
     internals:
       h ms = resolution()
       P11th real = exp(-h / tau_1)
       P22th real = exp(-h / tau_2)
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end
     input:
       ex_spikes pA <-excitatory spike
       in_spikes pA <-inhibitory spike
       I_stim pA <-current
     end

     output: spike

     update:

       /* evolve membrane potential*/
       integrate_odes()

       /* evolve adaptive threshold*/
       V_th_alpha_1 = V_th_alpha_1 * P11th
       V_th_alpha_2 = V_th_alpha_2 * P22th
       if r == 0: # not refractory
         if V_abs >= omega + V_th_alpha_1 + V_th_alpha_2: # threshold crossing
           r = RefractoryCounts

           /* procedure for adaptive potential*/
           V_th_alpha_1 += alpha_1 # short time
           V_th_alpha_2 += alpha_2 # long time
           emit_spike()
         end
       else:
         r = r - 1
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: mat2_psc_exp_characterisation.rst


.. footer::

   Generated at 2020-05-27 18:26:45.498666

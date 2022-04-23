aeif_cond_exp
#############


aeif_cond_exp - Conductance based exponential integrate-and-fire neuron model

Description
+++++++++++

aeif_cond_exp is the adaptive exponential integrate and fire neuron
according to Brette and Gerstner (2005), with post-synaptic
conductances in the form of truncated exponentials.

The membrane potential is given by the following differential equation:

.. math::

   C_m \frac{dV_m}{dt} =
   -g_L(V_m-E_L)+g_L\Delta_T\exp\left(\frac{V_m-V_{th}}{\Delta_T}\right) - g_e(t)(V_m-E_e) \\
                                                     -g_i(t)(V_m-E_i)-w +I_e

and

.. math::

   \tau_w \frac{dw}{dt} = a(V_m-E_L) - w

Note that the membrane potential can diverge to positive infinity due to the exponential term. To avoid numerical instabilities, instead of :math:`V_m`, the value :math:`\min(V_m,V_{peak})` is used in the dynamical equations.


References
++++++++++

.. [1] Brette R and Gerstner W (2005). Adaptive exponential
       integrate-and-fire model as an effective description of neuronal
       activity. Journal of Neurophysiology. 943637-3642
       DOI: https://doi.org/10.1152/jn.00686.2005


See also
++++++++

iaf_cond_exp, aeif_cond_alpha



Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "C_m", "pF", "281.0pF", "membrane parametersMembrane Capacitance"    
    "t_ref", "ms", "0.0ms", "Refractory period"    
    "V_reset", "mV", "-60.0mV", "Reset Potential"    
    "g_L", "nS", "30.0nS", "Leak Conductance"    
    "E_L", "mV", "-70.6mV", "Leak reversal Potential (aka resting potential)"    
    "a", "nS", "4nS", "spike adaptation parametersSubthreshold adaptation"    
    "b", "pA", "80.5pA", "Spike-triggered adaptation"    
    "Delta_T", "mV", "2.0mV", "Slope factor"    
    "tau_w", "ms", "144.0ms", "Adaptation time constant"    
    "V_th", "mV", "-50.4mV", "Threshold Potential"    
    "V_peak", "mV", "0mV", "Spike detection threshold"    
    "E_exc", "mV", "0mV", "synaptic parametersExcitatory reversal Potential"    
    "tau_syn_exc", "ms", "0.2ms", "Synaptic Time Constant Excitatory Synapse"    
    "E_inh", "mV", "-85.0mV", "Inhibitory reversal Potential"    
    "tau_syn_inh", "ms", "2.0ms", "Synaptic Time Constant for Inhibitory Synapse"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "E_L", "Membrane potential"    
    "w", "pA", "0pA", "Spike-adaptation current"




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-g_{L} \cdot (V_{bounded} - E_{L}) + I_{spike} - I_{syn,exc} - I_{syn,inh} - w + I_{e} + I_{stim}) } \right) 


.. math::
   \frac{ dw } { dt }= \frac 1 { \tau_{w} } \left( { (a \cdot (V_{bounded} - E_{L}) - w) } \right) 





Source code
+++++++++++

.. code-block:: nestml

   neuron aeif_cond_exp:
     state:
       V_m mV = E_L # Membrane potential
       w pA = 0pA # Spike-adaptation current
     end
     equations:
       inline V_bounded mV = min(V_m,V_peak) # prevent exponential divergence
       kernel g_inh = exp(-t / tau_syn_inh)
       kernel g_exc = exp(-t / tau_syn_exc)
       # Add inlines to simplify the equation definition of V_m
       inline exp_arg real = (V_bounded - V_th) / Delta_T
       inline I_spike pA = g_L * Delta_T * exp(exp_arg)
       inline I_syn_exc pA = convolve(g_exc,exc_spikes) * (V_bounded - E_exc)
       inline I_syn_inh pA = convolve(g_inh,inh_spikes) * (V_bounded - E_inh)
       V_m'=(-g_L * (V_bounded - E_L) + I_spike - I_syn_exc - I_syn_inh - w + I_e + I_stim) / C_m
       w'=(a * (V_bounded - E_L) - w) / tau_w
     end

     parameters:
       # membrane parameters
       C_m pF = 281.0pF # Membrane Capacitance
       t_ref ms = 0.0ms # Refractory period
       V_reset mV = -60.0mV # Reset Potential
       g_L nS = 30.0nS # Leak Conductance
       E_L mV = -70.6mV # Leak reversal Potential (aka resting potential)
       # spike adaptation parameters

       # spike adaptation parameters
       a nS = 4nS # Subthreshold adaptation
       b pA = 80.5pA # Spike-triggered adaptation
       Delta_T mV = 2.0mV # Slope factor
       tau_w ms = 144.0ms # Adaptation time constant
       V_th mV = -50.4mV # Threshold Potential
       V_peak mV = 0mV # Spike detection threshold
       # synaptic parameters

       # synaptic parameters
       E_exc mV = 0mV # Excitatory reversal Potential
       tau_syn_exc ms = 0.2ms # Synaptic Time Constant Excitatory Synapse
       E_inh mV = -85.0mV # Inhibitory reversal Potential
       tau_syn_inh ms = 2.0ms # Synaptic Time Constant for Inhibitory Synapse
       # constant external input current

       # constant external input current
       I_e pA = 0pA
     end
     internals:
       # refractory time in steps
       RefractoryCounts integer = steps(t_ref)
       # counts number of tick during the refractory period

       # counts number of tick during the refractory period
       r integer 
     end
     input:
       inh_spikes nS <-inhibitory spike
       exc_spikes nS <-excitatory spike
       I_stim pA <-current
     end

     output: spike

     update:
       integrate_odes()
       if r > 0: # refractory
         r -= 1 # decrement refractory ticks count
         V_m = V_reset # clamp potential
       elif V_m >= V_peak:
         r = RefractoryCounts + 1
         V_m = V_reset # clamp potential
         w += b
         emit_spike()
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: aeif_cond_exp_characterisation.rst


.. footer::

   Generated at 2022-03-28 19:04:29.501988
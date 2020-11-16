aeif_cond_exp
#############

aeif_cond_exp - Conductance based exponential integrate-and-fire neuron model


Description
+++++++++++

aeif_cond_exp is the adaptive exponential integrate and fire neuron
according to Brette and Gerstner (2005), with post-synaptic
conductances in the form of truncated exponentials.

This implementation uses the embedded 4th order Runge-Kutta-Fehlberg
solver with adaptive stepsize to integrate the differential equation.

The membrane potential is given by the following differential equation:

.. math::

 C dV/dt= -g_L(V-E_L)+g_L*\Delta_T*\exp((V-V_T)/\Delta_T)-g_e(t)(V-E_e) \\
                                                     -g_i(t)(V-E_i)-w +I_e

and

.. math::

 \tau_w * dw/dt = a(V-E_L) - W

Note that the spike detection threshold :math:`V_{peak}` is automatically set to
:math:`V_th+10` mV to avoid numerical instabilites that may result from
setting :math:`V_{peak}` too high.


References
++++++++++

.. [1] Brette R and Gerstner W (2005). Adaptive Exponential
       Integrate-and-Fire Model as an Effective Description of Neuronal
       Activity. J Neurophysiol 94:3637-3642.
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
    "a", "nS", "4nS", "spike adaptation parametersSubthreshold adaptation."    
    "b", "pA", "80.5pA", "Spike-trigg_exred adaptation."    
    "Delta_T", "mV", "2.0mV", "Slope factor"    
    "tau_w", "ms", "144.0ms", "Adaptation time constant"    
    "V_th", "mV", "-50.4mV", "Threshold Potential"    
    "V_peak", "mV", "0mV", "Spike detection threshold."    
    "E_ex", "mV", "0mV", "synaptic parametersExcitatory reversal Potential"    
    "tau_syn_ex", "ms", "0.2ms", "Synaptic Time Constant Excitatory Synapse"    
    "E_in", "mV", "-85.0mV", "Inhibitory reversal Potential"    
    "tau_syn_in", "ms", "2.0ms", "Synaptic Time Constant for Inhibitory Synapse"    
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

.. code:: nestml

   neuron aeif_cond_exp:
     initial_values:
       V_m mV = E_L # Membrane potential
       w pA = 0pA # Spike-adaptation current
     end
     equations:
       function V_bounded mV = min(V_m,V_peak) # prevent exponential divergence
       kernel g_in = exp(-1 / tau_syn_in * t)
       kernel g_ex = exp(-1 / tau_syn_ex * t)

       /* Add aliases to simplify the equation definition of V_m*/
       function exp_arg real = (V_bounded - V_th) / Delta_T
       function I_spike pA = g_L * Delta_T * exp(exp_arg)
       function I_syn_exc pA = convolve(g_ex,spikeExc) * (V_bounded - E_ex)
       function I_syn_inh pA = convolve(g_in,spikeInh) * (V_bounded - E_in)
       V_m'=(-g_L * (V_bounded - E_L) + I_spike - I_syn_exc - I_syn_inh - w + I_e + I_stim) / C_m
       w'=(a * (V_bounded - E_L) - w) / tau_w
     end

     parameters:

       /* membrane parameters*/
       C_m pF = 281.0pF # Membrane Capacitance
       t_ref ms = 0.0ms # Refractory period
       V_reset mV = -60.0mV # Reset Potential
       g_L nS = 30.0nS # Leak Conductance
       E_L mV = -70.6mV # Leak reversal Potential (aka resting potential)

       /* spike adaptation parameters*/
       a nS = 4nS # Subthreshold adaptation.
       b pA = 80.5pA # Spike-trigg_exred adaptation.
       Delta_T mV = 2.0mV # Slope factor
       tau_w ms = 144.0ms # Adaptation time constant
       V_th mV = -50.4mV # Threshold Potential
       V_peak mV = 0mV # Spike detection threshold.

       /* synaptic parameters*/
       E_ex mV = 0mV # Excitatory reversal Potential
       tau_syn_ex ms = 0.2ms # Synaptic Time Constant Excitatory Synapse
       E_in mV = -85.0mV # Inhibitory reversal Potential
       tau_syn_in ms = 2.0ms # Synaptic Time Constant for Inhibitory Synapse

       /* constant external input current*/
       I_e pA = 0pA
     end
     internals:

       /* refractory time in steps*/
       RefractoryCounts integer = steps(t_ref)
       /* counts number of tick during the refractory period*/

       /* counts number of tick during the refractory period*/
       r integer 
     end
     input:
       spikeInh nS <-inhibitory spike
       spikeExc nS <-excitatory spike
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

   Generated at 2020-05-27 18:26:45.193728
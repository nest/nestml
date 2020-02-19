aeif_cond_alpha_implicit_nestml
===============================


Name: aeif_cond_alpha_implicit -  Conductance based exponential integrate-and-fire neuron
                         model according to Brette and Gerstner (2005).

Description:
aeif_cond_alpha is the adaptive exponential integrate and fire neuron according
to Brette and Gerstner (2005).
Synaptic conductances are modelled as alpha-functions.

This implementation uses the embedded 4th order Runge-Kutta-Fehlberg solver with
adaptive step size to integrate the differential equation.

The membrane potential is given by the following differential equation:
C dV/dt= -g_L(V-E_L)+g_L*Delta_T*exp((V-V_T)/Delta_T)-g_e(t)(V-E_e)
                                                     -g_i(t)(V-E_i)-w + I_e + I_stim

and

tau_w * dw/dt= a(V-E_L) -W

Author: Marc-Oliver Gewaltig

Sends: SpikeEvent

Receives: SpikeEvent, CurrentEvent, DataLoggingRequest

References: Brette R and Gerstner W (2005) Adaptive Exponential
            Integrate-and-Fire Model as an Effective Description of Neuronal
            Activity. J Neurophysiol 94:3637-3642

SeeAlso: iaf_cond_alpha, aeif_cond_exp




Parameters
----------



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "C_m", "pF", "281.0pF", "
     membrane parameters
     Membrane Capacitance"    
    "t_ref", "ms", "0.0ms", "
     Refractory period"    
    "V_reset", "mV", "-60.0mV", "
     Reset Potential"    
    "g_L", "nS", "30.0nS", "
     Leak Conductance"    
    "E_L", "mV", "-70.6mV", "
     Leak reversal Potential (aka resting potential)"    
    "a", "nS", "4nS", "
     spike adaptation parameters
     Subthreshold adaptation"    
    "b", "pA", "80.5pA", "
     Spike-triggered adaptation"    
    "Delta_T", "mV", "2.0mV", "
     Slope factor"    
    "tau_w", "ms", "144.0ms", "
     Adaptation time constant"    
    "V_th", "mV", "-50.4mV", "
     Threshold Potential"    
    "V_peak", "mV", "0mV", "
     Spike detection threshold"    
    "E_ex", "mV", "0mV", "
     synaptic parameters
     Excitatory reversal Potential"    
    "tau_syn_ex", "ms", "0.2ms", "
     Synaptic Time Constant Excitatory Synapse"    
    "E_in", "mV", "-85.0mV", "
     Inhibitory reversal Potential"    
    "tau_syn_in", "ms", "2.0ms", "
     Synaptic Time Constant for Inhibitory Synapse"    
    "I_e", "pA", "0pA", "
     constant external input current
    None"




State variables
---------------

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "E_L", "
     Membrane potential"    
    "w", "pA", "0pA", "
     Spike-adaptation current"    
    "g_in", "nS", "0nS", "
     Excitatory synaptic conductance"    
    "g_in__d", "nS / ms", "nS * e / tau_syn_in", "
     Excitatory synaptic conductance"    
    "g_ex", "nS", "0nS", "
     Inhibitory synaptic conductance"    
    "g_ex__d", "nS / ms", "nS * e / tau_syn_ex", "
     Inhibitory synaptic conductance"




Equations
---------




.. math::
   \frac{ dV_m } { dt }= \frac 1 { C_{m} } \left( { (-g_{L} \cdot (V_{bounded} - E_{L}) + I_{spike} - I_{syn,exc} - I_{syn,inh} - w + I_{e} + I_{stim}) } \right) 


.. math::
   \frac{ dw } { dt }= \frac 1 { \tau_{w} } \left( { (a \cdot (V_{bounded} - E_{L}) - w) } \right) 





Source code
-----------

.. code:: nestml

   """
   Name: aeif_cond_alpha -  Conductance based exponential integrate-and-fire neuron
                            model according to Brette and Gerstner (2005).

   Description:
   aeif_cond_alpha is the adaptive exponential integrate and fire neuron according
   to Brette and Gerstner (2005).
   Synaptic conductances are modelled as alpha-functions.

   This implementation uses the embedded 4th order Runge-Kutta-Fehlberg solver with
   adaptive step size to integrate the differential equation.

   The membrane potential is given by the following differential equation:
   C dV/dt= -g_L(V-E_L)+g_L*Delta_T*exp((V-V_T)/Delta_T)-g_e(t)(V-E_e)
                                                        -g_i(t)(V-E_i)-w + I_e + I_stim

   and

   tau_w * dw/dt= a(V-E_L) -W

   Author: Marc-Oliver Gewaltig

   Sends: SpikeEvent

   Receives: SpikeEvent, CurrentEvent, DataLoggingRequest

   References: Brette R and Gerstner W (2005) Adaptive Exponential
               Integrate-and-Fire Model as an Effective Description of Neuronal
               Activity. J Neurophysiol 94:3637-3642

   SeeAlso: iaf_cond_alpha, aeif_cond_exp
   """
   neuron aeif_cond_alpha:

     initial_values:
       V_m mV = E_L      # Membrane potential
       w pA = 0 pA        # Spike-adaptation current
     end

     equations:
       function V_bounded mV = min(V_m, V_peak) # prevent exponential divergence
       shape g_in = (e/tau_syn_in) * t * exp(-t/tau_syn_in)
       shape g_ex = (e/tau_syn_ex) * t * exp(-t/tau_syn_ex)

       # Add functions to simplify the equation definition of V_m
       function exp_arg real = (V_bounded-V_th)/Delta_T
       function I_spike pA = g_L*Delta_T*exp(exp_arg)
       function I_syn_exc pA =   convolve(g_ex, spikesExc) * ( V_bounded - E_ex )
       function I_syn_inh pA =   convolve(g_in, spikesInh) * ( V_bounded - E_in )

       V_m' = ( -g_L*( V_bounded - E_L ) + I_spike - I_syn_exc - I_syn_inh - w + I_e + I_stim ) / C_m
       w' = (a*(V_m - E_L) - w)/tau_w
     end

     parameters:
       # membrane parameters
       C_m   pF = 281.0 pF       # Membrane Capacitance
       t_ref ms = 0.0 ms         # Refractory period
       V_reset mV = -60.0 mV     # Reset Potential
       g_L nS = 30.0 nS          # Leak Conductance
       E_L mV = -70.6 mV         # Leak reversal Potential (aka resting potential)

       # spike adaptation parameters
       a nS = 4 nS               # Subthreshold adaptation
       b pA = 80.5 pA            # pike-triggered adaptation
       Delta_T mV = 2.0 mV       # Slope factor
       tau_w ms = 144.0 ms       # Adaptation time constant
       V_th mV = -50.4 mV        # Threshold Potential
       V_peak mV = 0 mV          # Spike detection threshold

       # synaptic parameters
       E_ex mV = 0 mV            # Excitatory reversal Potential
       tau_syn_ex ms = 0.2 ms    # Synaptic Time Constant Excitatory Synapse
       E_in mV = -85.0 mV        # Inhibitory reversal Potential
       tau_syn_in ms = 2.0 ms    # Synaptic Time Constant for Inhibitory Synapse

       # constant external input current
       I_e pA = 0 pA
     end

     internals:
       # Impulse to add to DG_EXC on spike arrival to evoke unit-amplitude
       # conductance excursion.
       PSConInit_E nS/ms = nS * e / tau_syn_ex

       # Impulse to add to DG_INH on spike arrival to evoke unit-amplitude
       # conductance excursion.
       PSConInit_I nS/ms = nS * e / tau_syn_in

       # refractory time in steps
       RefractoryCounts integer = steps(t_ref)
       # counts number of tick during the refractory period
       r integer
     end

     input:
       spikesInh nS  <- inhibitory spike
       spikesExc nS  <- excitatory spike
       I_stim pA <- current
     end

     output: spike

     update:
       integrate_odes()

       if r > 0: # refractory
         r = r - 1 # decrement refractory ticks count
         V_m = V_reset
       elif V_m >= V_peak: # threshold crossing detection
         r = RefractoryCounts
         V_m = V_reset # clamp potential
         w += b
         emit_spike()
       end

     end

   end

   """
   Name: aeif_cond_alpha_implicit -  Conductance based exponential integrate-and-fire neuron
                            model according to Brette and Gerstner (2005).

   Description:
   aeif_cond_alpha is the adaptive exponential integrate and fire neuron according
   to Brette and Gerstner (2005).
   Synaptic conductances are modelled as alpha-functions.

   This implementation uses the embedded 4th order Runge-Kutta-Fehlberg solver with
   adaptive step size to integrate the differential equation.

   The membrane potential is given by the following differential equation:
   C dV/dt= -g_L(V-E_L)+g_L*Delta_T*exp((V-V_T)/Delta_T)-g_e(t)(V-E_e)
                                                        -g_i(t)(V-E_i)-w + I_e + I_stim

   and

   tau_w * dw/dt= a(V-E_L) -W

   Author: Marc-Oliver Gewaltig

   Sends: SpikeEvent

   Receives: SpikeEvent, CurrentEvent, DataLoggingRequest

   References: Brette R and Gerstner W (2005) Adaptive Exponential
               Integrate-and-Fire Model as an Effective Description of Neuronal
               Activity. J Neurophysiol 94:3637-3642

   SeeAlso: iaf_cond_alpha, aeif_cond_exp
   """
   neuron aeif_cond_alpha_implicit:

     state:
       r integer              # counts number of tick during the refractory period
     end

     initial_values:
       V_m mV = E_L           # Membrane potential
       w pA = 0 pA            # Spike-adaptation current
       g_in nS = 0 nS         # Excitatory synaptic conductance
       g_in' nS/ms = nS * e / tau_syn_in  # Excitatory synaptic conductance
       g_ex nS = 0 nS         # Inhibitory synaptic conductance
       g_ex' nS/ms = nS * e / tau_syn_ex  # Inhibitory synaptic conductance
     end

     equations:
       function V_bounded mV = min(V_m, V_peak) # prevent exponential divergence
       # alpha function for the g_in
       shape g_in'' = (-2/tau_syn_in) * g_in'-(1/tau_syn_in**2) * g_in

       # alpha function for the g_ex
       shape g_ex'' = (-2/tau_syn_ex) * g_ex'-(1/tau_syn_ex**2) * g_ex

       # Add aliases to simplify the equation definition of V_m
       function exp_arg real = (V_bounded-V_th)/Delta_T
       function I_spike pA = g_L*Delta_T*exp(exp_arg)
       function I_syn_exc pA =   convolve(g_ex, spikesExc) * ( V_bounded - E_ex )
       function I_syn_inh pA =   convolve(g_in, spikesInh) * ( V_bounded - E_in )

       V_m' = ( -g_L*( V_bounded - E_L ) + I_spike - I_syn_exc - I_syn_inh - w + I_e + I_stim ) / C_m
       w' = (a*(V_bounded - E_L) - w)/tau_w
     end

     parameters:
       # membrane parameters
       C_m pF = 281.0 pF         # Membrane Capacitance
       t_ref ms = 0.0 ms         # Refractory period
       V_reset mV = -60.0 mV     # Reset Potential
       g_L nS = 30.0 nS          # Leak Conductance
       E_L mV = -70.6 mV         # Leak reversal Potential (aka resting potential)

       # spike adaptation parameters
       a nS = 4 nS               # Subthreshold adaptation
       b pA = 80.5 pA            # Spike-triggered adaptation
       Delta_T mV = 2.0 mV       # Slope factor
       tau_w ms = 144.0 ms       # Adaptation time constant
       V_th mV = -50.4 mV        # Threshold Potential
       V_peak mV = 0 mV          # Spike detection threshold

       # synaptic parameters
       E_ex mV = 0 mV            # Excitatory reversal Potential
       tau_syn_ex ms = 0.2 ms    # Synaptic Time Constant Excitatory Synapse
       E_in mV = -85.0 mV        # Inhibitory reversal Potential
       tau_syn_in ms = 2.0 ms    # Synaptic Time Constant for Inhibitory Synapse

       # constant external input current
       I_e pA = 0 pA
     end

     internals:
       # refractory time in steps
       RefractoryCounts integer = steps(t_ref)
     end

     input:
       spikesInh nS  <- inhibitory spike
       spikesExc nS  <- excitatory spike
       I_stim pA <- current
     end

     output: spike

     update:
       integrate_odes()

       if r > 0: # refractory
         r -= 1 # decrement refractory ticks count
         V_m = V_reset # clamp potential
       elif V_m >= V_peak: # threshold crossing detection
         r = RefractoryCounts
         V_m = V_reset # clamp potential
         w += b
         emit_spike()
       end

     end

   end




.. footer::

   Generated at 2020-02-19 20:31:20.998659
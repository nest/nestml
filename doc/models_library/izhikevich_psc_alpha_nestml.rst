izhikevich_psc_alpha_nestml
###########################

Name: izhikevich_psc_alpha - Detailed Izhikevich neuron model with alpha-shaped
                             post-synaptic current.

Description:
Implementation of the simple spiking neuron model introduced by Izhikevich
[1]. The dynamics are given by:
   C_m dV_m/dt = k (V-V_t)(V-V_t) - u + I + I_syn_ex + I_syn_in
   dU_m/dt = a*(b*(V_m-E_L) - U_m)

   if v >= V_th:
     V_m is set to c
     U_m is incremented by d

   On each spike arrival, the membrane potential feels an alpha-shaped current
   of the form:
     I_syn = I_0 * t * exp(-t/tau_syn) / tau_syn.

References:
[1] Izhikevich, Simple Model of Spiking Neurons,
IEEE Transactions on Neural Networks (2003) 14:1569-1572

Sends: SpikeEvent

Receives: SpikeEvent, CurrentEvent, DataLoggingRequest
FirstVersion: 2009
Author: Hanuschkin, Morrison, Kunkel
SeeAlso: izhikevitch, iaf_psc_alpha, mat2_psc_alpha



Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto    
    "C_m", "pF", "200.0pF", "Membrane capacitance"    
    "k", "pF / (ms mV)", "8.0pF / mV / ms", "Spiking slope"    
    "V_r", "mV", "-65.0mV", "resting potential"    
    "V_t", "mV", "-45.0mV", "threshold potential"    
    "a", "1 / ms", "0.01 / ms", "describes time scale of recovery variable"    
    "b", "nS", "9.0nS", "sensitivity of recovery variable"    
    "c", "mV", "-65mV", "after-spike reset value of V_m"    
    "d", "pA", "60.0pA", "after-spike reset value of U_m"    
    "V_peak", "mV", "0.0mV", "Spike detection threashold (reset condition"    
    "tau_syn_ex", "ms", "0.2ms", "Synaptic Time Constant Excitatory Synapse"    
    "tau_syn_in", "ms", "2.0ms", "Synaptic Time Constant for Inhibitory Synapse"    
    "t_ref", "ms", "2.0ms", "Refractory period"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto    
    "V_m", "mV", "-65mV", "Membrane potential"    
    "U_m", "pA", "0pA", "Membrane potential recovery variable"




Equations
+++++++++




.. math::
   \frac{ dV_{m}' } { dt }= \frac 1 { C_{m} } \left( { (k \cdot (V_{m} - V_{r}) \cdot (V_{m} - V_{t}) - U_{m} + I_{e} + I_{stim} + I_{syn,inh} + I_{syn,exc}) } \right) 


.. math::
   \frac{ dU_{m}' } { dt }= a \cdot (b \cdot (V_{m} - V_{r}) - U_{m})





Source code
+++++++++++

.. code:: nestml

   """
   Name: izhikevich_psc_alpha - Detailed Izhikevich neuron model with alpha-shaped
                                post-synaptic current.

   Description:
   Implementation of the simple spiking neuron model introduced by Izhikevich
   [1]. The dynamics are given by:
      C_m dV_m/dt = k (V-V_t)(V-V_t) - u + I + I_syn_ex + I_syn_in
      dU_m/dt = a*(b*(V_m-E_L) - U_m)

      if v >= V_th:
        V_m is set to c
        U_m is incremented by d

      On each spike arrival, the membrane potential feels an alpha-shaped current
      of the form:
        I_syn = I_0 * t * exp(-t/tau_syn) / tau_syn.

   References:
   [1] Izhikevich, Simple Model of Spiking Neurons,
   IEEE Transactions on Neural Networks (2003) 14:1569-1572

   Sends: SpikeEvent

   Receives: SpikeEvent, CurrentEvent, DataLoggingRequest
   FirstVersion: 2009
   Author: Hanuschkin, Morrison, Kunkel
   SeeAlso: izhikevitch, iaf_psc_alpha, mat2_psc_alpha
   """

   neuron izhikevich_psc_alpha:

     state:
       r integer # number of steps in the current refractory phase
     end

     initial_values:
       V_m mV = -65 mV # Membrane potential
       U_m pA = 0 pA   # Membrane potential recovery variable
     end

     equations:
       # synapses: alpha functions
       shape I_syn_in = (e/tau_syn_in) * t * exp(-t/tau_syn_in)
       shape I_syn_ex = (e/tau_syn_ex) * t * exp(-t/tau_syn_ex)

       function I_syn_exc pA = convolve(I_syn_ex, spikesExc)
       function I_syn_inh pA = convolve(I_syn_in, spikesInh)

       V_m' = ( k * (V_m - V_r) * (V_m - V_t) - U_m + I_e + I_stim + I_syn_inh + I_syn_exc ) / C_m
       U_m' = a * ( b*(V_m - V_r) - U_m )
     end

     parameters:
       C_m pF = 200. pF           # Membrane capacitance
       k pF/mV/ms = 8. pF/mV/ms   # Spiking slope
       V_r mV = -65. mV           # resting potential
       V_t mV = -45. mV           # threshold potential
       a 1/ms = 0.01 /ms          # describes time scale of recovery variable
       b nS = 9. nS               # sensitivity of recovery variable
       c mV = -65 mV              # after-spike reset value of V_m
       d pA = 60. pA              # after-spike reset value of U_m
       V_peak mV = 0. mV          # Spike detection threashold (reset condition)
       tau_syn_ex ms = 0.2 ms     # Synaptic Time Constant Excitatory Synapse
       tau_syn_in ms = 2.0 ms     # Synaptic Time Constant for Inhibitory Synapse
       t_ref ms = 2.0 ms          # Refractory period

       # constant external input current
       I_e pA = 0 pA
     end

     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end

     input:
       spikesInh pA <- inhibitory spike
       spikesExc pA <- excitatory spike
       I_stim pA <- current
     end

     output: spike

     update:
       integrate_odes()

       # refractoriness and threshold crossing
       if r > 0: # is refractory?
         r -= 1
       elif V_m >= V_peak:
         V_m = c
         U_m += d
         emit_spike()
         r = RefractoryCounts
       end

     end

   end

   """
   Name: izhikevich_psc_alpha_implicit - Detailed Izhikevich neuron model with
                                         alpha-shaped post-synaptic current.

   Description:
   Implementation of the simple spiking neuron model introduced by Izhikevich
   [1]. The dynamics are given by:
      C_m dV_m/dt = k (V-V_t)(V-V_t) - u + I + I_syn_ex + I_syn_in
      dU_m/dt = a*(b*(V_m-E_L) - U_m)

      if v >= V_th:
        V_m is set to c
        U_m is incremented by d

      On each spike arrival, the membrane potential feels an alpha-shaped current
      of the form:
        I_syn = I_0 * t * exp(-t/tau_syn) / tau_syn.

   References:
   [1] Izhikevich, Simple Model of Spiking Neurons,
   IEEE Transactions on Neural Networks (2003) 14:1569-1572

   Sends: SpikeEvent

   Receives: SpikeEvent, CurrentEvent, DataLoggingRequest
   FirstVersion: 2009
   Author: Hanuschkin, Morrison, Kunkel
   SeeAlso: izhikevitch, iaf_psc_alpha, mat2_psc_alpha
   """

   neuron izhikevich_psc_alpha_implicit:

     state:
       r integer # number of steps in the current refractory phase
     end

     initial_values:
       V_m mV = -65 mV                        # Membrane potential
       U_m pA = 0 pA                          # Membrane potential recovery variable
       I_syn_ex pA = 0. pA                    # inputs from the exc conductance
       I_syn_ex' pA/ms = pA * e / tau_syn_in  # inputs from the exc conductance
       I_syn_in pA = 0 pA                      # inputs from the inh conductance
       I_syn_in' pA/ms = pA * e / tau_syn_in  # inputs from the inh conductance
     end

     equations:
       # synapses: alpha functions

       # alpha function for the g_in
       shape I_syn_in'' = (-2/tau_syn_in) * I_syn_in'-(1/tau_syn_in**2) * I_syn_in

       # alpha function for the g_ex
       shape I_syn_ex'' = (-2/tau_syn_ex) * I_syn_ex'-(1/tau_syn_ex**2) * I_syn_ex

       function I_syn_exc pA = convolve(I_syn_ex, spikesExc)
       function I_syn_inh pA = convolve(I_syn_in, spikesInh)

       V_m' = ( k * (V_m - V_r) * (V_m - V_t) - U_m + I_e + I_stim + I_syn_inh + I_syn_exc ) / C_m
       U_m' = a * ( b*(V_m - V_r) - U_m )
     end

     parameters:
       C_m pF = 200. pF           # Membrane capacitance
       k pF/mV/ms = 8. pF/mV/ms   # Spiking slope
       V_r mV = -65. mV           # resting potential
       V_t mV = -45. mV           # threshold potential
       a 1/ms = 0.01 /ms          # describes time scale of recovery variable
       b nS = 9. nS               # sensitivity of recovery variable
       c mV = -65 mV              # after-spike reset value of V_m
       d pA = 60. pA              # after-spike reset value of U_m
       V_peak mV = 0. mV          # Spike detection threshold (reset condition)
       tau_syn_ex ms = 0.2 ms     # Synaptic Time Constant Excitatory Synapse
       tau_syn_in ms = 2.0 ms     # Synaptic Time Constant for Inhibitory Synapse
       t_ref ms = 2.0 ms          # Refractory period

       # constant external input current
       I_e pA = 0 pA
     end

     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end

     input:
       spikesInh pA <- inhibitory spike
       spikesExc pA <- excitatory spike
       I_stim pA <- current
     end

     output: spike

     update:
       integrate_odes()

       # refractoriness and threshold crossing
       if r > 0: # is refractory?
         r -= 1
       elif V_m >= V_peak:
         V_m = c
         U_m += d
         emit_spike()
         r = RefractoryCounts
       end

     end

   end




.. footer::

   Generated at 2020-02-21 11:18:26.068990
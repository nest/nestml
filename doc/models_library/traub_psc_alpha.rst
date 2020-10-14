traub_psc_alpha
###############

Name: traub_psc_alpha - Traub model according to Borgers 2017.

Reduced Traub-Miles Model of a Pyramidal Neuron in Rat Hippocampus[1].
parameters got from reference [2].

(1) Post-synaptic currents
 Incoming spike events induce a post-synaptic change of current modelled
 by an alpha function.

(2) Spike Detection
 Spike detection is done by a combined threshold-and-local-maximum search: if
 there is a local maximum above a certain threshold of the membrane potential,
 it is considered a spike.


References:

[1] R. D. Traub and R. Miles, Neuronal Networks of the Hippocampus,Cam- bridge University Press, Cambridge, UK, 1991.
[2] Borgers, C., 2017. An introduction to modeling neuronal dynamics (Vol. 66). Cham: Springer.


SeeAlso: hh_cond_exp_traub


Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "t_ref", "ms", "2.0ms", "Refractory period 2.0"    
    "g_Na", "nS", "10000.0nS", "Sodium peak conductance"    
    "g_K", "nS", "8000.0nS", "Potassium peak conductance"    
    "g_L", "nS", "10nS", "Leak conductance"    
    "C_m", "pF", "100.0pF", "Membrane Capacitance"    
    "E_Na", "mV", "50.0mV", "Sodium reversal potential"    
    "E_K", "mV", "-100.0mV", "Potassium reversal potentia"    
    "E_L", "mV", "-67.0mV", "Leak reversal Potential (aka resting potential)"    
    "V_Tr", "mV", "-20.0mV", "Spike Threshold"    
    "tau_syn_ex", "ms", "0.2ms", "Rise time of the excitatory synaptic alpha function i"    
    "tau_syn_in", "ms", "2.0ms", "Rise time of the inhibitory synaptic alpha function"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "-70.0mV", "Membrane potential"    
    "alpha_n_init", "real", "0.032 * (V_m / mV + 52.0) / (1.0 - exp(-(V_m / mV + 52.0) / 5.0))", ""    
    "beta_n_init", "real", "0.5 * exp(-(V_m / mV + 57.0) / 40.0)", ""    
    "alpha_m_init", "real", "0.32 * (V_m / mV + 54.0) / (1.0 - exp(-(V_m / mV + 54.0) / 4.0))", ""    
    "beta_m_init", "real", "0.28 * (V_m / mV + 27.0) / (exp((V_m / mV + 27.0) / 5.0) - 1.0)", ""    
    "alpha_h_init", "real", "0.128 * exp(-(V_m / mV + 50.0) / 18.0)", ""    
    "beta_h_init", "real", "4.0 / (1.0 + exp(-(V_m / mV + 27.0) / 5.0))", ""    
    "Act_m", "real", "alpha_m_init / (alpha_m_init + beta_m_init)", "Activation variable m for Na"    
    "Inact_h", "real", "alpha_h_init / (alpha_h_init + beta_h_init)", "Inactivation variable h for Na"    
    "Act_n", "real", "alpha_n_init / (alpha_n_init + beta_n_init)", "Activation variable n for K"




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-(I_{Na} + I_{K} + I_{L}) + I_{e} + I_{stim} + I_{syn,inh} + I_{syn,exc}) } \right) 


.. math::
   \frac{ dAct_{n} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{n} \cdot (1 - Act_{n}) - \beta_{n} \cdot Act_{n}) } \right) 


.. math::
   \frac{ dAct_{m} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{m} \cdot (1 - Act_{m}) - \beta_{m} \cdot Act_{m}) } \right) 


.. math::
   \frac{ dInact_{h} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{h} \cdot (1 - Inact_{h}) - \beta_{h} \cdot Inact_{h}) } \right) 





Source code
+++++++++++

.. code:: nestml

   neuron traub_psc_alpha:
     state:
       r integer  # number of steps in the current refractory phase
     end
     initial_values:
       V_m mV = -70.0mV # Membrane potential
       function alpha_n_init real = 0.032 * (V_m / mV + 52.0) / (1.0 - exp(-(V_m / mV + 52.0) / 5.0))
       function beta_n_init real = 0.5 * exp(-(V_m / mV + 57.0) / 40.0)
       function alpha_m_init real = 0.32 * (V_m / mV + 54.0) / (1.0 - exp(-(V_m / mV + 54.0) / 4.0))
       function beta_m_init real = 0.28 * (V_m / mV + 27.0) / (exp((V_m / mV + 27.0) / 5.0) - 1.0)
       function alpha_h_init real = 0.128 * exp(-(V_m / mV + 50.0) / 18.0)
       function beta_h_init real = 4.0 / (1.0 + exp(-(V_m / mV + 27.0) / 5.0))
       Act_m real = alpha_m_init / (alpha_m_init + beta_m_init) # Activation variable m for Na
       Inact_h real = alpha_h_init / (alpha_h_init + beta_h_init) # Inactivation variable h for Na
       Act_n real = alpha_n_init / (alpha_n_init + beta_n_init) # Activation variable n for K
     end
     equations:

       /* synapses: alpha functions*/
       kernel I_syn_in = (e / tau_syn_in) * t * exp(-t / tau_syn_in)
       kernel I_syn_ex = (e / tau_syn_ex) * t * exp(-t / tau_syn_ex)
       function I_syn_exc pA = convolve(I_syn_ex,spikeExc)
       function I_syn_inh pA = convolve(I_syn_in,spikeInh)
       function I_Na pA = g_Na * Act_m * Act_m * Act_m * Inact_h * (V_m - E_Na)
       function I_K pA = g_K * Act_n * Act_n * Act_n * Act_n * (V_m - E_K)
       function I_L pA = g_L * (V_m - E_L)
       V_m'=(-(I_Na + I_K + I_L) + I_e + I_stim + I_syn_inh + I_syn_exc) / C_m

       /* Act_n*/
       function alpha_n real = 0.032 * (V_m / mV + 52.0) / (1.0 - exp(-(V_m / mV + 52.0) / 5.0))
       function beta_n real = 0.5 * exp(-(V_m / mV + 57.0) / 40.0)
       Act_n'=(alpha_n * (1 - Act_n) - beta_n * Act_n) / ms # n-variable

       /* Act_m*/
       function alpha_m real = 0.32 * (V_m / mV + 54.0) / (1.0 - exp(-(V_m / mV + 54.0) / 4.0))
       function beta_m real = 0.28 * (V_m / mV + 27.0) / (exp((V_m / mV + 27.0) / 5.0) - 1.0)
       Act_m'=(alpha_m * (1 - Act_m) - beta_m * Act_m) / ms # m-variable

       /* Inact_h'*/
       function alpha_h real = 0.128 * exp(-(V_m / mV + 50.0) / 18.0)
       function beta_h real = 4.0 / (1.0 + exp(-(V_m / mV + 27.0) / 5.0))
       Inact_h'=(alpha_h * (1 - Inact_h) - beta_h * Inact_h) / ms # h-variable
     end

     parameters:
       t_ref ms = 2.0ms # Refractory period 2.0
       g_Na nS = 10000.0nS # Sodium peak conductance
       g_K nS = 8000.0nS # Potassium peak conductance
       g_L nS = 10nS # Leak conductance
       C_m pF = 100.0pF # Membrane Capacitance
       E_Na mV = 50.0mV # Sodium reversal potential
       E_K mV = -100.0mV # Potassium reversal potentia
       E_L mV = -67.0mV # Leak reversal Potential (aka resting potential)
       V_Tr mV = -20.0mV # Spike Threshold
       tau_syn_ex ms = 0.2ms # Rise time of the excitatory synaptic alpha function i
       tau_syn_in ms = 2.0ms # Rise time of the inhibitory synaptic alpha function

       /* constant external input current*/
       I_e pA = 0pA
     end
     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
     end
     input:
       spikeInh pA <-inhibitory spike
       spikeExc pA <-excitatory spike
       I_stim pA <-current
     end

     output: spike

     update:
       U_old mV = V_m
       integrate_odes()
       /* sending spikes: crossing 0 mV, pseudo-refractoriness and local maximum...*/

       /* sending spikes: crossing 0 mV, pseudo-refractoriness and local maximum...*/
       if r > 0: # is refractory?
         r -= 1
       elif V_m > V_Tr and U_old > V_Tr:
         r = RefractoryCounts
         emit_spike()
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: traub_psc_alpha_characterisation.rst


.. footer::

   Generated at 2020-05-27 18:26:45.520049
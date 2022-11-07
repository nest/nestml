traub_psc_alpha
###############


traub_psc_alpha - Traub model according to Borgers 2017

Reduced Traub-Miles Model of a Pyramidal Neuron in Rat Hippocampus [1]_.
parameters got from reference [2]_.

Incoming spike events induce a post-synaptic change of current modelled
by an alpha function.

References
++++++++++

.. [1] R. D. Traub and R. Miles, Neuronal Networks of the Hippocampus,Cam- bridge University Press, Cambridge, UK, 1991.
.. [2] Borgers, C., 2017. An introduction to modeling neuronal dynamics (Vol. 66). Cham: Springer.


See also
++++++++

hh_cond_exp_traub



Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "t_ref", "ms", "2ms", "Refractory period"    
    "g_Na", "nS", "10000nS", "Sodium peak conductance"    
    "g_K", "nS", "8000nS", "Potassium peak conductance"    
    "g_L", "nS", "10nS", "Leak conductance"    
    "C_m", "pF", "100pF", "Membrane capacitance"    
    "E_Na", "mV", "50mV", "Sodium reversal potential"    
    "E_K", "mV", "-100mV", "Potassium reversal potential"    
    "E_L", "mV", "-67mV", "Leak reversal potential (aka resting potential)"    
    "V_Tr", "mV", "-20mV", "Spike threshold"    
    "tau_syn_exc", "ms", "0.2ms", "Rise time of the excitatory synaptic alpha function"    
    "tau_syn_inh", "ms", "2ms", "Rise time of the inhibitory synaptic alpha function"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "number of steps in the current refractory phase"    
    "V_m", "mV", "-70.0mV", "Membrane potential"    
    "Act_m", "real", "alpha_m_init / (alpha_m_init + beta_m_init)", "Activation variable m for Na"    
    "Inact_h", "real", "alpha_h_init / (alpha_h_init + beta_h_init)", "Inactivation variable h for Na"    
    "Act_n", "real", "alpha_n_init / (alpha_n_init + beta_n_init)", "Activation variable n for K"




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-(I_{Na} + I_{K} + I_{L}) + I_{e} + I_{stim} + I_{syn,exc} - I_{syn,inh}) } \right) 


.. math::
   \frac{ dAct_{n} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{n} \cdot (1 - Act_{n}) - \beta_{n} \cdot Act_{n}) } \right) 


.. math::
   \frac{ dAct_{m} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{m} \cdot (1 - Act_{m}) - \beta_{m} \cdot Act_{m}) } \right) 


.. math::
   \frac{ dInact_{h} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{h} \cdot (1 - Inact_{h}) - \beta_{h} \cdot Inact_{h}) } \right) 





Source code
+++++++++++

.. code-block:: nestml

   neuron traub_psc_alpha:
     state:
       r integer = 0 # number of steps in the current refractory phase
       V_m mV = -70.0mV # Membrane potential
       Act_m real = alpha_m_init / (alpha_m_init + beta_m_init) # Activation variable m for Na
       Inact_h real = alpha_h_init / (alpha_h_init + beta_h_init) # Inactivation variable h for Na
       Act_n real = alpha_n_init / (alpha_n_init + beta_n_init) # Activation variable n for K
     end
     equations:
       # synapses: alpha functions
       kernel K_syn_inh = (e / tau_syn_inh) * t * exp(-t / tau_syn_inh)
       kernel K_syn_exc = (e / tau_syn_exc) * t * exp(-t / tau_syn_exc)
       inline I_syn_exc pA = convolve(K_syn_exc,exc_spikes)
       inline I_syn_inh pA = convolve(K_syn_inh,inh_spikes)
       inline I_Na pA = g_Na * Act_m * Act_m * Act_m * Inact_h * (V_m - E_Na)
       inline I_K pA = g_K * Act_n * Act_n * Act_n * Act_n * (V_m - E_K)
       inline I_L pA = g_L * (V_m - E_L)
       V_m'=(-(I_Na + I_K + I_L) + I_e + I_stim + I_syn_exc - I_syn_inh) / C_m
       # Act_n
       inline alpha_n real = 0.032 * (V_m / mV + 52.0) / (1.0 - exp(-(V_m / mV + 52.0) / 5.0))
       inline beta_n real = 0.5 * exp(-(V_m / mV + 57.0) / 40.0)
       Act_n'=(alpha_n * (1 - Act_n) - beta_n * Act_n) / ms # n-variable
       # Act_m

       # Act_m
       inline alpha_m real = 0.32 * (V_m / mV + 54.0) / (1.0 - exp(-(V_m / mV + 54.0) / 4.0))
       inline beta_m real = 0.28 * (V_m / mV + 27.0) / (exp((V_m / mV + 27.0) / 5.0) - 1.0)
       Act_m'=(alpha_m * (1 - Act_m) - beta_m * Act_m) / ms # m-variable
       # Inact_h'

       # Inact_h'
       inline alpha_h real = 0.128 * exp(-(V_m / mV + 50.0) / 18.0)
       inline beta_h real = 4.0 / (1.0 + exp(-(V_m / mV + 27.0) / 5.0))
       Inact_h'=(alpha_h * (1 - Inact_h) - beta_h * Inact_h) / ms # h-variable
     end

     parameters:
       t_ref ms = 2ms # Refractory period
       g_Na nS = 10000nS # Sodium peak conductance
       g_K nS = 8000nS # Potassium peak conductance
       g_L nS = 10nS # Leak conductance
       C_m pF = 100pF # Membrane capacitance
       E_Na mV = 50mV # Sodium reversal potential
       E_K mV = -100mV # Potassium reversal potential
       E_L mV = -67mV # Leak reversal potential (aka resting potential)
       V_Tr mV = -20mV # Spike threshold
       tau_syn_exc ms = 0.2ms # Rise time of the excitatory synaptic alpha function
       tau_syn_inh ms = 2ms # Rise time of the inhibitory synaptic alpha function
       # constant external input current

       # constant external input current
       I_e pA = 0pA
     end
     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
       alpha_n_init real = 0.032 * (V_m / mV + 52.0) / (1.0 - exp(-(V_m / mV + 52.0) / 5.0))
       beta_n_init real = 0.5 * exp(-(V_m / mV + 57.0) / 40.0)
       alpha_m_init real = 0.32 * (V_m / mV + 54.0) / (1.0 - exp(-(V_m / mV + 54.0) / 4.0))
       beta_m_init real = 0.28 * (V_m / mV + 27.0) / (exp((V_m / mV + 27.0) / 5.0) - 1.0)
       alpha_h_init real = 0.128 * exp(-(V_m / mV + 50.0) / 18.0)
       beta_h_init real = 4.0 / (1.0 + exp(-(V_m / mV + 27.0) / 5.0))
     end
     input:
       inh_spikes pA <-inhibitory spike
       exc_spikes pA <-excitatory spike
       I_stim pA <-current
     end

     output: spike

     update:
       U_old mV = V_m
       integrate_odes()
       # sending spikes: crossing 0 mV, pseudo-refractoriness and local maximum...

       # sending spikes: crossing 0 mV, pseudo-refractoriness and local maximum...
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

   Generated at 2022-03-28 19:04:29.609967
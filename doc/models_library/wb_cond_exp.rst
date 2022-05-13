wb_cond_exp
###########


wb_cond_exp - Wang-Buzsaki model

Description
+++++++++++

wb_cond_exp is an implementation of a modified Hodkin-Huxley model.

(1) Post-synaptic currents: Incoming spike events induce a post-synaptic change
    of conductance modeled by an exponential function.

(2) Spike Detection: Spike detection is done by a combined threshold-and-local-
    maximum search: if there is a local maximum above a certain threshold of
    the membrane potential, it is considered a spike.

References
++++++++++

.. [1] Wang, X.J. and Buzsaki, G., (1996) Gamma oscillation by synaptic
       inhibition in a hippocampal interneuronal network model. Journal of
       neuroscience, 16(20), pp.6402-6413.

See Also
++++++++

hh_cond_exp_traub, wb_cond_multisyn



Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "t_ref", "ms", "2ms", "Refractory period"    
    "g_Na", "nS", "3500nS", "Sodium peak conductance"    
    "g_K", "nS", "900nS", "Potassium peak conductance"    
    "g_L", "nS", "10nS", "Leak conductance"    
    "C_m", "pF", "100pF", "Membrane capacitance"    
    "E_Na", "mV", "55mV", "Sodium reversal potential"    
    "E_K", "mV", "-90mV", "Potassium reversal potential"    
    "E_L", "mV", "-65mV", "Leak reversal potential (aka resting potential)"    
    "V_Tr", "mV", "-55mV", "Spike threshold"    
    "tau_syn_exc", "ms", "0.2ms", "Rise time of the excitatory synaptic alpha function"    
    "tau_syn_inh", "ms", "10ms", "Rise time of the inhibitory synaptic alpha function"    
    "E_exc", "mV", "0mV", "Excitatory synaptic reversal potential"    
    "E_inh", "mV", "-75mV", "Inhibitory synaptic reversal potential"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "number of steps in the current refractory phase"    
    "V_m", "mV", "E_L", "Membrane potential"    
    "Inact_h", "real", "alpha_h_init / (alpha_h_init + beta_h_init)", ""    
    "Act_n", "real", "alpha_n_init / (alpha_n_init + beta_n_init)", ""




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-(I_{Na} + I_{K} + I_{L}) + I_{e} + I_{stim} + I_{syn,exc} - I_{syn,inh}) } \right) 


.. math::
   \frac{ dAct_{n} } { dt }= (alpha_n(V_{m}) \cdot (1 - Act_{n}) - beta_n(V_{m}) \cdot Act_{n})


.. math::
   \frac{ dInact_{h} } { dt }= (alpha_h(V_{m}) \cdot (1 - Inact_{h}) - beta_h(V_{m}) \cdot Inact_{h})





Source code
+++++++++++

.. code-block:: nestml

   neuron wb_cond_exp:
     state:
       r integer = 0 # number of steps in the current refractory phase
       V_m mV = E_L # Membrane potential
       Inact_h real = alpha_h_init / (alpha_h_init + beta_h_init)
       Act_n real = alpha_n_init / (alpha_n_init + beta_n_init)
     end
     equations:
       # synapses: exponential conductance
       kernel g_inh = exp(-t / tau_syn_inh)
       kernel g_exc = exp(-t / tau_syn_exc)
   recordable    inline I_syn_exc pA = convolve(g_exc,exc_spikes) * (V_m - E_exc)
   recordable    inline I_syn_inh pA = convolve(g_inh,inh_spikes) * (V_m - E_inh)
       inline I_Na pA = g_Na * _subexpr(V_m) * Inact_h * (V_m - E_Na)
       inline I_K pA = g_K * Act_n ** 4 * (V_m - E_K)
       inline I_L pA = g_L * (V_m - E_L)
       V_m'=(-(I_Na + I_K + I_L) + I_e + I_stim + I_syn_exc - I_syn_inh) / C_m
       Act_n'=(alpha_n(V_m) * (1 - Act_n) - beta_n(V_m) * Act_n) # n-variable
       Inact_h'=(alpha_h(V_m) * (1 - Inact_h) - beta_h(V_m) * Inact_h) # h-variable
     end

     parameters:
       t_ref ms = 2ms # Refractory period
       g_Na nS = 3500nS # Sodium peak conductance
       g_K nS = 900nS # Potassium peak conductance
       g_L nS = 10nS # Leak conductance
       C_m pF = 100pF # Membrane capacitance
       E_Na mV = 55mV # Sodium reversal potential
       E_K mV = -90mV # Potassium reversal potential
       E_L mV = -65mV # Leak reversal potential (aka resting potential)
       V_Tr mV = -55mV # Spike threshold
       tau_syn_exc ms = 0.2ms # Rise time of the excitatory synaptic alpha function
       tau_syn_inh ms = 10ms # Rise time of the inhibitory synaptic alpha function
       E_exc mV = 0mV # Excitatory synaptic reversal potential
       E_inh mV = -75mV # Inhibitory synaptic reversal potential
       # constant external input current

       # constant external input current
       I_e pA = 0pA
     end
     internals:
       RefractoryCounts integer = steps(t_ref) # refractory time in steps
       alpha_n_init 1/ms = -0.05 / (ms * mV) * (E_L + 34.0mV) / (exp(-0.1 * (E_L + 34.0mV)) - 1.0)
       beta_n_init 1/ms = 0.625 / ms * exp(-(E_L + 44.0mV) / 80.0mV)
       alpha_h_init 1/ms = 0.35 / ms * exp(-(E_L + 58.0mV) / 20.0mV)
       beta_h_init 1/ms = 5.0 / (exp(-0.1 / mV * (E_L + 28.0mV)) + 1.0) / ms
     end
     input:
       inh_spikes nS <-inhibitory spike
       exc_spikes nS <-excitatory spike
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
       elif V_m > V_Tr and U_old > V_m:
         r = RefractoryCounts
         emit_spike()
       end
     end

   function _subexpr(V_m mV) real:
       return alpha_m(V_m) ** 3 / (alpha_m(V_m) + beta_m(V_m)) ** 3
   end

   function alpha_m(V_m mV) 1/ms:
       return 0.1 / (ms * mV) * (V_m + 35.0mV) / (1.0 - exp(-0.1mV * (V_m + 35.0mV)))
   end

   function beta_m(V_m mV) 1/ms:
       return 4.0 / (ms) * exp(-(V_m + 60.0mV) / 18.0mV)
   end

   function alpha_n(V_m mV) 1/ms:
       return -0.05 / (ms * mV) * (V_m + 34.0mV) / (exp(-0.1 * (V_m + 34.0mV)) - 1.0)
   end

   function beta_n(V_m mV) 1/ms:
       return 0.625 / ms * exp(-(V_m + 44.0mV) / 80.0mV)
   end

   function alpha_h(V_m mV) 1/ms:
       return 0.35 / ms * exp(-(V_m + 58.0mV) / 20.0mV)
   end

   function beta_h(V_m mV) 1/ms:
       return 5.0 / (exp(-0.1 / mV * (V_m + 28.0mV)) + 1.0) / ms
   end

   end



Characterisation
++++++++++++++++

.. include:: wb_cond_exp_characterisation.rst


.. footer::

   Generated at 2022-03-28 19:04:29.829103
hh_cond_exp_traub
#################


hh_cond_exp_traub - Hodgkin-Huxley model for Brette et al (2007) review

Description
+++++++++++

hh_cond_exp_traub is an implementation of a modified Hodgkin-Huxley model.

This model was specifically developed for a major review of simulators [1]_,
based on a model of hippocampal pyramidal cells by Traub and Miles [2]_.
The key differences between the current model and the model in [2]_ are:

- This model is a point neuron, not a compartmental model.
- This model includes only I_Na and I_K, with simpler I_K dynamics than
  in [2]_, so it has only three instead of eight gating variables;
  in particular, all Ca dynamics have been removed.
- Incoming spikes induce an instantaneous conductance change followed by
  exponential decay instead of activation over time.

This model is primarily provided as reference implementation for hh_coba
example of the Brette et al (2007) review. Default parameter values are chosen
to match those used with NEST 1.9.10 when preparing data for [1]_. Code for all
simulators covered is available from ModelDB [3]_.

Note: In this model, a spike is emitted if :math:`V_m >= V_T + 30` mV and
:math:`V_m` has fallen during the current time step.

To avoid that this leads to multiple spikes during the falling flank of a
spike, it is essential to choose a sufficiently long refractory period.
Traub and Miles used :math:`t_{ref} = 3` ms [2, p 118], while we used
:math:`t_{ref} = 2` ms in [2]_.

References
++++++++++

.. [1] Brette R et al. (2007). Simulation of networks of spiking neurons: A
       review of tools and strategies. Journal of Computational Neuroscience
       23:349-98. DOI: https://doi.org/10.1007/s10827-007-0038-6
.. [2] Traub RD and Miles R (1991). Neuronal networks of the hippocampus.
       Cambridge University Press, Cambridge UK.
.. [3] http://modeldb.yale.edu/83319


See also
++++++++

hh_psc_alpha



Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "g_Na", "nS", "20000nS", "Na Conductance"    
    "g_K", "nS", "6000nS", "K Conductance"    
    "g_L", "nS", "10nS", "Leak Conductance"    
    "C_m", "pF", "200pF", "Membrane Capacitance"    
    "E_Na", "mV", "50mV", "Reversal potentials"    
    "E_K", "mV", "-90mV", "Potassium reversal potential"    
    "E_L", "mV", "-60mV", "Leak reversal potential (aka resting potential)"    
    "V_T", "mV", "-63mV", "Voltage offset that controls dynamics. For default"    
    "tau_syn_exc", "ms", "5ms", "parameters, V_T = -63 mV results in a threshold around -50 mV.Synaptic time constant of excitatory synapse"    
    "tau_syn_inh", "ms", "10ms", "Synaptic time constant of inhibitory synapse"    
    "t_ref", "ms", "2ms", "Refractory period"    
    "E_exc", "mV", "0mV", "Excitatory synaptic reversal potential"    
    "E_inh", "mV", "-80mV", "Inhibitory synaptic reversal potential"    
    "alpha_n_init", "1 / ms", "0.032 / (ms * mV) * (15.0mV - E_L) / (exp((15.0mV - E_L) / 5.0mV) - 1.0)", ""    
    "beta_n_init", "1 / ms", "0.5 / ms * exp((10.0mV - E_L) / 40.0mV)", ""    
    "alpha_m_init", "1 / ms", "0.32 / (ms * mV) * (13.0mV - E_L) / (exp((13.0mV - E_L) / 4.0mV) - 1.0)", ""    
    "beta_m_init", "1 / ms", "0.28 / (ms * mV) * (E_L - 40.0mV) / (exp((E_L - 40.0mV) / 5.0mV) - 1.0)", ""    
    "alpha_h_init", "1 / ms", "0.128 / ms * exp((17.0mV - E_L) / 18.0mV)", ""    
    "beta_h_init", "1 / ms", "(4.0 / (1.0 + exp((40.0mV - E_L) / 5.0mV))) / ms", ""    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "counts number of tick during the refractory period"    
    "V_m", "mV", "E_L", "Membrane potential"    
    "Act_m", "real", "alpha_m_init / (alpha_m_init + beta_m_init)", ""    
    "Act_h", "real", "alpha_h_init / (alpha_h_init + beta_h_init)", ""    
    "Inact_n", "real", "alpha_n_init / (alpha_n_init + beta_n_init)", ""




Equations
+++++++++




.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-I_{Na} - I_{K} - I_{L} - I_{syn,exc} - I_{syn,inh} + I_{e} + I_{stim}) } \right) 


.. math::
   \frac{ dAct_{m} } { dt }= (\alpha_{m} - (\alpha_{m} + \beta_{m}) \cdot Act_{m})


.. math::
   \frac{ dAct_{h} } { dt }= (\alpha_{h} - (\alpha_{h} + \beta_{h}) \cdot Act_{h})


.. math::
   \frac{ dInact_{n} } { dt }= (\alpha_{n} - (\alpha_{n} + \beta_{n}) \cdot Inact_{n})





Source code
+++++++++++

.. code-block:: nestml

   neuron hh_cond_exp_traub:
     state:
       r integer = 0 # counts number of tick during the refractory period
       V_m mV = E_L # Membrane potential
       Act_m real = alpha_m_init / (alpha_m_init + beta_m_init)
       Act_h real = alpha_h_init / (alpha_h_init + beta_h_init)
       Inact_n real = alpha_n_init / (alpha_n_init + beta_n_init)
     end
     equations:
       # synapses: exponential conductance
       kernel g_inh = exp(-t / tau_syn_inh)
       kernel g_exc = exp(-t / tau_syn_exc)
       # Add aliases to simplify the equation definition of V_m
       inline I_Na pA = g_Na * Act_m * Act_m * Act_m * Act_h * (V_m - E_Na)
       inline I_K pA = g_K * Inact_n * Inact_n * Inact_n * Inact_n * (V_m - E_K)
       inline I_L pA = g_L * (V_m - E_L)
       inline I_syn_exc pA = convolve(g_exc,exc_spikes) * (V_m - E_exc)
       inline I_syn_inh pA = convolve(g_inh,inh_spikes) * (V_m - E_inh)
       V_m'=(-I_Na - I_K - I_L - I_syn_exc - I_syn_inh + I_e + I_stim) / C_m
       # channel dynamics
       inline V_rel mV = V_m - V_T
       inline alpha_n 1/ms = 0.032 / (ms * mV) * (15.0mV - V_rel) / (exp((15.0mV - V_rel) / 5.0mV) - 1.0)
       inline beta_n 1/ms = 0.5 / ms * exp((10.0mV - V_rel) / 40.0mV)
       inline alpha_m 1/ms = 0.32 / (ms * mV) * (13.0mV - V_rel) / (exp((13.0mV - V_rel) / 4.0mV) - 1.0)
       inline beta_m 1/ms = 0.28 / (ms * mV) * (V_rel - 40.0mV) / (exp((V_rel - 40.0mV) / 5.0mV) - 1.0)
       inline alpha_h 1/ms = 0.128 / ms * exp((17.0mV - V_rel) / 18.0mV)
       inline beta_h 1/ms = (4.0 / (1.0 + exp((40.0mV - V_rel) / 5.0mV))) / ms
       Act_m'=(alpha_m - (alpha_m + beta_m) * Act_m)
       Act_h'=(alpha_h - (alpha_h + beta_h) * Act_h)
       Inact_n'=(alpha_n - (alpha_n + beta_n) * Inact_n)
     end

     parameters:
       g_Na nS = 20000nS # Na Conductance
       g_K nS = 6000nS # K Conductance
       g_L nS = 10nS # Leak Conductance
       C_m pF = 200pF # Membrane Capacitance
       E_Na mV = 50mV # Reversal potentials
       E_K mV = -90mV # Potassium reversal potential
       E_L mV = -60mV # Leak reversal potential (aka resting potential)
       V_T mV = -63mV # Voltage offset that controls dynamics. For default
       # parameters, V_T = -63 mV results in a threshold around -50 mV.

       # parameters, V_T = -63 mV results in a threshold around -50 mV.
       tau_syn_exc ms = 5ms # Synaptic time constant of excitatory synapse
       tau_syn_inh ms = 10ms # Synaptic time constant of inhibitory synapse
       t_ref ms = 2ms # Refractory period
       E_exc mV = 0mV # Excitatory synaptic reversal potential
       E_inh mV = -80mV # Inhibitory synaptic reversal potential
       alpha_n_init 1/ms = 0.032 / (ms * mV) * (15.0mV - E_L) / (exp((15.0mV - E_L) / 5.0mV) - 1.0)
       beta_n_init 1/ms = 0.5 / ms * exp((10.0mV - E_L) / 40.0mV)
       alpha_m_init 1/ms = 0.32 / (ms * mV) * (13.0mV - E_L) / (exp((13.0mV - E_L) / 4.0mV) - 1.0)
       beta_m_init 1/ms = 0.28 / (ms * mV) * (E_L - 40.0mV) / (exp((E_L - 40.0mV) / 5.0mV) - 1.0)
       alpha_h_init 1/ms = 0.128 / ms * exp((17.0mV - E_L) / 18.0mV)
       beta_h_init 1/ms = (4.0 / (1.0 + exp((40.0mV - E_L) / 5.0mV))) / ms
       # constant external input current
       I_e pA = 0pA
     end
     internals:
       RefractoryCounts integer = steps(t_ref)
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
       if r > 0:
         r -= 1
       elif V_m > V_T + 30mV and U_old > V_m:
         r = RefractoryCounts
         emit_spike()
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: hh_cond_exp_traub_characterisation.rst


.. footer::

   Generated at 2022-03-28 19:04:29.349088
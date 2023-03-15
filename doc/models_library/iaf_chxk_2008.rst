iaf_chxk_2008
#############


iaf_chxk_2008 - Conductance based leaky integrate-and-fire neuron model used in Casti et al. 2008

Description
+++++++++++

iaf_chxk_2008 is an implementation of a spiking neuron using IAF dynamics with
conductance-based synapses [1]_. A spike is emitted when the membrane potential
is crossed from below. After a spike, an afterhyperpolarizing (AHP) conductance
is activated which repolarizes the neuron over time. Membrane potential is not
reset explicitly and the model also has no explicit refractory time.

The AHP conductance and excitatory and inhibitory synaptic input conductances
follow alpha-function time courses as in the iaf_cond_alpha model.

.. note ::
   In the original Fortran implementation underlying [1]_, all previous AHP activation was discarded when a new spike
   occurred, leading to reduced AHP currents in particular during periods of high spiking activity. Set ``ahp_bug`` to
   ``true`` to obtain this behavior in the model.


References
++++++++++

.. [1] Casti A, Hayot F, Xiao Y, Kaplan E (2008) A simple model of retina-LGN
       transmission. Journal of Computational Neuroscience 24:235-252.
       DOI: https://doi.org/10.1007/s10827-007-0053-7


See also
++++++++

iaf_cond_alpha



Parameters
++++++++++



.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_th", "mV", "-45.0mV", "Threshold potential"    
    "E_exc", "mV", "20mV", "Excitatory reversal potential"    
    "E_inh", "mV", "-90mV", "Inhibitory reversal potential"    
    "g_L", "nS", "100nS", "Leak conductance"    
    "C_m", "pF", "1000.0pF", "Membrane capacitance"    
    "E_L", "mV", "-60.0mV", "Leak reversal Potential (aka resting potential)"    
    "tau_syn_exc", "ms", "1ms", "Synaptic time constant of excitatory synapse"    
    "tau_syn_inh", "ms", "1ms", "Synaptic time constant of inhibitory synapse"    
    "tau_ahp", "ms", "0.5ms", "Afterhyperpolarization (AHP) time constant"    
    "G_ahp", "nS", "443.8nS", "AHP conductance"    
    "E_ahp", "mV", "-95mV", "AHP potential"    
    "ahp_bug", "boolean", "false", "If true, discard AHP conductance value from previous spikes"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "E_L", "membrane potential"    
    "g_ahp", "nS", "0nS", "AHP conductance"    
    "g_ahp", "nS / ms", "0nS / ms", "AHP conductance"




Equations
+++++++++




.. math::
   \frac{ d^2 g_{ahp} } { dt^2 }= \frac{ -2 \cdot g_{ahp}' } { \tau_{ahp} } - \frac{ g_{ahp} } { { \tau_{ahp} }^{ 2 } }


.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-I_{leak} - I_{syn,exc} - I_{syn,inh} - I_{ahp} + I_{e} + I_{stim}) } \right) 





Source code
+++++++++++

.. code-block:: nestml

   neuron iaf_chxk_2008:
     state:
       V_m mV = E_L # membrane potential
       g_ahp nS = 0nS # AHP conductance
       g_ahp' nS/ms = 0nS / ms # AHP conductance
     end
     equations:
       kernel g_inh = (e / tau_syn_inh) * t * exp(-t / tau_syn_inh)
       kernel g_exc = (e / tau_syn_exc) * t * exp(-t / tau_syn_exc)
       g_ahp''=-2 * g_ahp' / tau_ahp - g_ahp / tau_ahp ** 2
       inline I_syn_exc pA = convolve(g_exc,exc_spikes) * (V_m - E_exc)
       inline I_syn_inh pA = convolve(g_inh,inh_spikes) * (V_m - E_inh)
       inline I_ahp pA = g_ahp * (V_m - E_ahp)
       inline I_leak pA = g_L * (V_m - E_L)
       V_m'=(-I_leak - I_syn_exc - I_syn_inh - I_ahp + I_e + I_stim) / C_m
     end

     parameters:
       V_th mV = -45.0mV # Threshold potential
       E_exc mV = 20mV # Excitatory reversal potential
       E_inh mV = -90mV # Inhibitory reversal potential
       g_L nS = 100nS # Leak conductance
       C_m pF = 1000.0pF # Membrane capacitance
       E_L mV = -60.0mV # Leak reversal Potential (aka resting potential)
       tau_syn_exc ms = 1ms # Synaptic time constant of excitatory synapse
       tau_syn_inh ms = 1ms # Synaptic time constant of inhibitory synapse
       tau_ahp ms = 0.5ms # Afterhyperpolarization (AHP) time constant
       G_ahp nS = 443.8nS # AHP conductance
       E_ahp mV = -95mV # AHP potential
       ahp_bug boolean = false # If true, discard AHP conductance value from previous spikes
       # constant external input current

       # constant external input current
       I_e pA = 0pA
     end
     internals:
       # Impulse to add to DG_EXC on spike arrival to evoke unit-amplitude conductance excursion.
       PSConInit_E nS/ms = nS * e / tau_syn_exc
       # Impulse to add to DG_INH on spike arrival to evoke unit-amplitude conductance excursion.
       PSConInit_I nS/ms = nS * e / tau_syn_inh
       PSConInit_AHP real = G_ahp * e / tau_ahp * (ms / nS)
     end
     input:
       inh_spikes nS <-inhibitory spike
       exc_spikes nS <-excitatory spike
       I_stim pA <-current
     end

     output: spike

     update:
       vm_prev mV = V_m
       integrate_odes()
       if vm_prev < V_th and V_m >= V_th:
         # Find precise spike time using linear interpolation
         sigma real = (V_m - V_th) * resolution() / (V_m - vm_prev) / ms
         alpha real = exp(-sigma / tau_ahp)
         delta_g_ahp real = PSConInit_AHP * sigma * alpha
         delta_dg_ahp real = PSConInit_AHP * alpha
         if ahp_bug == true:
           # Bug in original code ignores AHP conductance from previous spikes
           g_ahp = delta_g_ahp * nS
           g_ahp' = delta_dg_ahp * nS / ms
         else:
           # Correct implementation adds initial values for new AHP to AHP history
           g_ahp += delta_g_ahp * nS
           g_ahp' += delta_dg_ahp * nS / ms
         end
         emit_spike()
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: iaf_chxk_2008_characterisation.rst


.. footer::

   Generated at 2022-03-28 19:04:29.728109
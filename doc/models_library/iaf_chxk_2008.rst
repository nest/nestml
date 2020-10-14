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

    
    "V_th", "mV", "-45.0mV", "Threshold Potential"    
    "E_ex", "mV", "20mV", "Excitatory reversal potential"    
    "E_in", "mV", "-90mV", "Inhibitory reversal potential"    
    "g_L", "nS", "100nS", "Leak Conductance"    
    "C_m", "pF", "1000.0pF", "Membrane Capacitance"    
    "E_L", "mV", "-60.0mV", "Leak reversal Potential (aka resting potential)"    
    "tau_syn_ex", "ms", "1ms", "Synaptic Time Constant Excitatory Synapse"    
    "tau_syn_in", "ms", "1ms", "Synaptic Time Constant for Inhibitory Synapse"    
    "tau_ahp", "ms", "0.5ms", "Afterhyperpolarization (AHP) time constant"    
    "g_ahp", "nS", "443.8nS", "AHP conductance"    
    "E_ahp", "mV", "-95mV", "AHP potential"    
    "ahp_bug", "boolean", "false", "If true, discard AHP conductance value from previous spikes"    
    "I_e", "pA", "0pA", "constant external input current"




State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "E_L", "membrane potential"    
    "G_ahp", "nS", "0nS", "AHP conductance"    
    "G_ahp__d", "nS / ms", "0nS / ms", "AHP conductance"




Equations
+++++++++




.. math::
   \frac{ dG_{ahp,,d} } { dt }= (\frac{ -2 } { \tau_{ahp} }) \cdot G_{ahp,,d} - (\frac{ 1 } { { \tau_{ahp} }^{ 2 } }) \cdot G_{ahp}


.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-I_{leak} - I_{syn,exc} - I_{syn,inh} - I_{ahp} + I_{e} + I_{stim}) } \right) 


.. math::
   \frac{ dG_{ahp} } { dt }= G_{ahp,,d}





Source code
+++++++++++

.. code:: nestml

   neuron iaf_chxk_2008:
     initial_values:
       V_m mV = E_L # membrane potential
       G_ahp nS = 0nS # AHP conductance
       G_ahp__d nS/ms = 0nS / ms # AHP conductance
       /*G_ahp' nS/ms = e / tau_ahp * nS    AHP conductance*/

     end
     equations:
       kernel g_in = (e / tau_syn_in) * t * exp(-t / tau_syn_in)
       kernel g_ex = (e / tau_syn_ex) * t * exp(-t / tau_syn_ex)
       G_ahp__d'=(-2 / tau_ahp) * G_ahp__d - (1 / tau_ahp ** 2) * G_ahp
       function I_syn_exc pA = convolve(g_ex,spikesExc) * (V_m - E_ex)
       function I_syn_inh pA = convolve(g_in,spikesInh) * (V_m - E_in)
       function I_ahp pA = G_ahp * (V_m - E_ahp)
       function I_leak pA = g_L * (V_m - E_L)
       V_m'=(-I_leak - I_syn_exc - I_syn_inh - I_ahp + I_e + I_stim) / C_m
       G_ahp'=G_ahp__d
     end

     parameters:
       V_th mV = -45.0mV # Threshold Potential
       E_ex mV = 20mV # Excitatory reversal potential
       E_in mV = -90mV # Inhibitory reversal potential
       g_L nS = 100nS # Leak Conductance
       C_m pF = 1000.0pF # Membrane Capacitance
       E_L mV = -60.0mV # Leak reversal Potential (aka resting potential)
       tau_syn_ex ms = 1ms # Synaptic Time Constant Excitatory Synapse
       tau_syn_in ms = 1ms # Synaptic Time Constant for Inhibitory Synapse
       tau_ahp ms = 0.5ms # Afterhyperpolarization (AHP) time constant
       g_ahp nS = 443.8nS # AHP conductance
       E_ahp mV = -95mV # AHP potential
       ahp_bug boolean = false # If true, discard AHP conductance value from previous spikes

       /* constant external input current*/
       I_e pA = 0pA
     end
     internals:

       /* Impulse to add to DG_EXC on spike arrival to evoke unit-amplitude*/
       /* conductance excursion.*/
       PSConInit_E nS/ms = nS * e / tau_syn_ex

       /* Impulse to add to DG_INH on spike arrival to evoke unit-amplitude*/
       /* conductance excursion.*/
       PSConInit_I nS/ms = nS * e / tau_syn_in
       PSConInit_AHP real = g_ahp * e / tau_ahp * (ms / nS)
     end
     input:
       spikesInh nS <-inhibitory spike
       spikesExc nS <-excitatory spike
       I_stim pA <-current
     end

     output: spike

     update:
       vm_prev mV = V_m
       integrate_odes()
       if vm_prev < V_th and V_m >= V_th:

         /* Find precise spike time using linear interpolation*/
         sigma real = (V_m - V_th) * resolution() / (V_m - vm_prev) / ms
         alpha real = exp(-sigma / tau_ahp)
         delta_g_ahp real = PSConInit_AHP * sigma * alpha
         delta_dg_ahp real = PSConInit_AHP * alpha
         if ahp_bug == true:

           /* Bug in original code ignores AHP conductance from previous spikes*/
           G_ahp = delta_g_ahp * nS
           G_ahp__d = delta_dg_ahp * nS / ms
         else:
           G_ahp += delta_g_ahp * nS
           G_ahp__d += delta_dg_ahp * nS / ms
         end
         emit_spike()
       end
     end

   end



Characterisation
++++++++++++++++

.. include:: iaf_chxk_2008_characterisation.rst


.. footer::

   Generated at 2020-05-27 18:26:44.567160
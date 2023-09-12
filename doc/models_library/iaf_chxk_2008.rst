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

The model source code can be found in the NESTML models repository here: `iaf_chxk_2008 <https://github.com/nest/nestml/tree/master/models/neurons/iaf_chxk_2008.nestml>`_.

Characterisation
++++++++++++++++

.. include:: iaf_chxk_2008_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.431863
iaf_cond_beta
#############


iaf_cond_beta - Simple conductance based leaky integrate-and-fire neuron model

Description
+++++++++++

iaf_cond_beta is an implementation of a spiking neuron using IAF dynamics with
conductance-based synapses. Incoming spike events induce a post-synaptic change
of conductance modelled by a beta function. The beta function
is normalised such that an event of weight 1.0 results in a peak current of
1 nS at :math:`t = \tau_{rise\_[ex|in]}`.


References
++++++++++

.. [1] Meffin H, Burkitt AN, Grayden DB (2004). An analytical
       model for the large, fluctuating synaptic conductance state typical of
       neocortical neurons in vivo. Journal of Computational Neuroscience,
       16:159-175.
       DOI: https://doi.org/10.1023/B:JCNS.0000014108.03012.81
.. [2] Bernander O, Douglas RJ, Martin KAC, Koch C (1991). Synaptic background
       activity influences spatiotemporal integration in single pyramidal
       cells.  Proceedings of the National Academy of Science USA,
       88(24):11569-11573.
       DOI: https://doi.org/10.1073/pnas.88.24.11569
.. [3] Kuhn A, Rotter S (2004) Neuronal integration of synaptic input in
       the fluctuation- driven regime. Journal of Neuroscience,
       24(10):2345-2356
       DOI: https://doi.org/10.1523/JNEUROSCI.3349-03.2004
.. [4] Rotter S,  Diesmann M (1999). Exact simulation of time-invariant linear
       systems with applications to neuronal modeling. Biologial Cybernetics
       81:381-402.
       DOI: https://doi.org/10.1007/s004220050570
.. [5] Roth A and van Rossum M (2010). Chapter 6: Modeling synapses.
       in De Schutter, Computational Modeling Methods for Neuroscientists,
       MIT Press.


See also
++++++++

iaf_cond_exp, iaf_cond_alpha



Parameters
++++++++++
.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "E_L", "mV", "-70mV", "Leak reversal potential (aka resting potential)"    
    "C_m", "pF", "250pF", "Capacitance of the membrane"    
    "t_ref", "ms", "2ms", "Refractory period"    
    "V_th", "mV", "-55mV", "Threshold potential"    
    "V_reset", "mV", "-60mV", "Reset potential"    
    "E_ex", "mV", "0mV", "Excitatory reversal potential"    
    "E_in", "mV", "-85mV", "Inhibitory reversal potential"    
    "g_L", "nS", "16.6667nS", "Leak conductance"    
    "tau_syn_rise_I", "ms", "0.2ms", "Synaptic time constant excitatory synapse"    
    "tau_syn_decay_I", "ms", "2ms", "Synaptic time constant for inhibitory synapse"    
    "tau_syn_rise_E", "ms", "0.2ms", "Synaptic time constant excitatory synapse"    
    "tau_syn_decay_E", "ms", "2ms", "Synaptic time constant for inhibitory synapse"    
    "F_E", "nS", "0nS", "Constant external input conductance (excitatory)."    
    "F_I", "nS", "0nS", "Constant external input conductance (inhibitory)."    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "r", "integer", "0", "counts number of tick during the refractory period"    
    "V_m", "mV", "E_L", "membrane potential"    
    "g_in", "real", "0", "inputs from the inhibitory conductance"    
    "g_in$", "real", "g_I_const * (1 / tau_syn_rise_I - 1 / tau_syn_decay_I)", ""    
    "g_ex", "real", "0", "inputs from the excitatory conductance"    
    "g_ex$", "real", "g_E_const * (1 / tau_syn_rise_E - 1 / tau_syn_decay_E)", ""




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-I_{leak} - I_{syn,exc} - I_{syn,inh} + I_{e} + I_{stim}) } \right) 



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `iaf_cond_beta <https://github.com/nest/nestml/tree/master/models/neurons/iaf_cond_beta.nestml>`_.

Characterisation
++++++++++++++++

.. include:: iaf_cond_beta_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.369517
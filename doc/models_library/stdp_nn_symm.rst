stdp_nn_symm
############


Synapse type for spike-timing dependent plasticity with symmetric nearest-neighbour spike pairing scheme

Description
+++++++++++

stdp_nn_symm_synapse is a connector to create synapses with spike time
dependent plasticity with the symmetric nearest-neighbour spike pairing
scheme [1]_.

When a presynaptic spike occurs, it is taken into account in the depression
part of the STDP weight change rule with the nearest preceding postsynaptic
one, and when a postsynaptic spike occurs, it is accounted in the
facilitation rule with the nearest preceding presynaptic one (instead of
pairing with all spikes, like in stdp_synapse). For a clear illustration of
this scheme see fig. 7A in [2]_.

The pairs exactly coinciding (so that presynaptic_spike == postsynaptic_spike
+ dendritic_delay), leading to zero delta_t, are discarded. In this case the
concerned pre/postsynaptic spike is paired with the second latest preceding
post/presynaptic one (for example, pre=={10 ms; 20 ms} and post=={20 ms} will
result in a potentiation pair 20-to-10).

The implementation involves two additional variables - presynaptic and
postsynaptic traces [2]_. The presynaptic trace decays exponentially over
time with the time constant tau_plus and increases to 1 on a pre-spike
occurrence. The postsynaptic trace (implemented on the postsynaptic neuron
side) decays with the time constant tau_minus and increases to 1 on a
post-spike occurrence.

.. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/fig/stdp-nearest-neighbour.png

   Figure 7 from Morrison, Diesmann and Gerstner

   Original caption:

   Phenomenological models of synaptic plasticity based on spike timing", Biological Cybernetics 98 (2008). "Examples of nearest neighbor spike pairing schemes for a pre-synaptic neuron j and a postsynaptic neuron i. In each case, the dark gray indicate which pairings contribute toward depression of a synapse, and light gray indicate which pairings contribute toward potentiation. **(a)** Symmetric interpretation: each presynaptic spike is paired with the last postsynaptic spike, and each postsynaptic spike is paired with the last presynaptic spike (Morrison et al. 2007). **(b)** Presynaptic centered interpretation: each presynaptic spike is paired with the last postsynaptic spike and the next postsynaptic spike (Izhikevich and Desai 2003; Burkitt et al. 2004: Model II). **(c)** Reduced symmetric interpretation: as in **(b)** but only for immediate pairings (Burkitt et al. 2004: Model IV, also implemented in hardware by Schemmel et al. 2006)

References
++++++++++

.. [1] Morrison A., Aertsen A., Diesmann M. (2007) Spike-timing dependent
       plasticity in balanced random networks, Neural Comput. 19:1437--1467

.. [2] Morrison A., Diesmann M., and Gerstner W. (2008) Phenomenological
       models of synaptic plasticity based on spike timing,
       Biol. Cybern. 98, 459--478



Parameters
++++++++++


.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "d", "ms", "1ms", "Synaptic transmission delay"    
    "lambda", "real", "0.01", ""    
    "tau_tr_pre", "ms", "20ms", ""    
    "tau_tr_post", "ms", "20ms", ""    
    "alpha", "real", "1.0", ""    
    "mu_plus", "real", "1.0", ""    
    "mu_minus", "real", "1.0", ""    
    "Wmax", "real", "100.0", ""    
    "Wmin", "real", "0.0", ""


State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "w", "real", "1.0", "Synaptic weight"    
    "pre_trace", "real", "0.0", ""    
    "post_trace", "real", "0.0", ""
Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `stdp_nn_symm <https://github.com/nest/nestml/tree/master/models/synapses/stdp_nn_symm.nestml>`_.


Characterisation
++++++++++++++++

.. include:: stdp_nn_symm_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.875577
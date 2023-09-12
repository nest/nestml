neuromodulated_stdp
###################


neuromodulated_stdp - Synapse model for spike-timing dependent plasticity modulated by a neurotransmitter such as dopamine

Description
+++++++++++

stdp_dopamine_synapse is a connection to create synapses with
dopamine-modulated spike-timing dependent plasticity (used as a
benchmark model in [1]_, based on [2]_). The dopaminergic signal is a
low-pass filtered version of the spike rate of a user-specific pool
of neurons. The spikes emitted by the pool of dopamine neurons are
delivered to the synapse via the assigned volume transmitter. The
dopaminergic dynamics is calculated in the synapse itself.

References
++++++++++
.. [1] Potjans W, Morrison A, Diesmann M (2010). Enabling functional neural
       circuit simulations with distributed computing of neuromodulated
       plasticity. Frontiers in Computational Neuroscience, 4:141.
       DOI: https://doi.org/10.3389/fncom.2010.00141
.. [2] Izhikevich EM (2007). Solving the distal reward problem through linkage
       of STDP and dopamine signaling. Cerebral Cortex, 17(10):2443-2452.
       DOI: https://doi.org/10.1093/cercor/bhl152



Parameters
++++++++++


.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "d", "ms", "1ms", "Synaptic transmission delay"    
    "tau_tr_pre", "ms", "20ms", "STDP time constant for weight changes caused by pre-before-post spike pairings."    
    "tau_tr_post", "ms", "20ms", "STDP time constant for weight changes caused by post-before-pre spike pairings."    
    "tau_c", "ms", "1000ms", "Time constant of eligibility trace"    
    "tau_n", "ms", "200ms", "Time constant of dopaminergic trace"    
    "b", "real", "0.0", "Dopaminergic baseline concentration"    
    "Wmax", "real", "200.0", "Maximal synaptic weight"    
    "Wmin", "real", "0.0", "Minimal synaptic weight"    
    "A_plus", "real", "1.0", "Multiplier applied to weight changes caused by pre-before-post spike pairings. If b (dopamine baseline concentration) is zero, then A_plus is simply the multiplier for facilitation (as in the stdp_synapse model). If b is not zero, then A_plus will be the multiplier for facilitation only if n - b is positive, where n is the instantenous dopamine concentration in the volume transmitter. If n - b is negative, A_plus will be the multiplier for depression."    
    "A_minus", "real", "1.5", "Multiplier applied to weight changes caused by post-before-pre spike pairings. If b (dopamine baseline concentration) is zero, then A_minus is simply the multiplier for depression (as in the stdp_synapse model). If b is not zero, then A_minus will be the multiplier for depression only if n - b is positive, where n is the instantenous dopamine concentration in the volume transmitter. If n - b is negative, A_minus will be the multiplier for facilitation."


State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "w", "real", "1.0", ""    
    "n", "real", "0.0", "Neuromodulator concentration"    
    "c", "real", "0.0", "Eligibility trace"    
    "pre_tr", "real", "0.0", ""    
    "post_tr", "real", "0.0", ""
Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `neuromodulated_stdp <https://github.com/nest/nestml/tree/master/models/synapses/neuromodulated_stdp.nestml>`_.


Characterisation
++++++++++++++++

.. include:: neuromodulated_stdp_characterisation.rst


.. footer::

   Generated at 2023-08-22 14:29:44.891623
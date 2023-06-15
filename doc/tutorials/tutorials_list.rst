Creating neuron models
----------------------

* :doc:`Izhikevich tutorial </tutorials/izhikevich/nestml_izhikevich_tutorial>`

  Learn how to write the Izhikevich spiking neuron model in NESTML.

* :doc:`Spike-frequency adaptation </tutorials/spike_frequency_adaptation/nestml_spike_frequency_adaptation_tutorial>`

  Spike-frequency adaptation (SFA) is the empirically observed phenomenon where the firing rate of a neuron decreases for a sustained, constant stimulus. Learn how to model SFA using threshold adaptation and an adaptation current.

* :doc:`Active dendrite tutorial </tutorials/active_dendrite/nestml_active_dendrite_tutorial>`

  Learn how to model a dendritic action potential in an existing NESTML neuron.

* :doc:`Ornstein-Uhlenbeck noise </tutorials/ornstein_uhlenbeck_noise/nestml_ou_noise_tutorial>`

  Implement the Ornstein-Uhlenbeck process in NESTML and use it to inject a noise current into a neuron.


Creating synapse models
-----------------------

* :doc:`STDP windows </tutorials/stdp_windows/stdp_windows>`

  An STDP window describes how the strength of the synapse changes as a function of the relative timing of pre- and postsynaptic spikes. Several different STDP model variants with different window functions are implemented.

* :doc:`Triplet STDP synapse </tutorials/triplet_stdp_synapse/triplet_stdp_synapse>`

  A triplet STDP rule is sensitive to third-order correlations of pre- and postsynaptic spike times, and accounts better for experimentally seen dependence on timing and frequency.

* :doc:`Dopamine-modulated STDP synapse </tutorials/stdp_dopa_synapse/stdp_dopa_synapse>`

  Adding dopamine modulation to the weight update rule of an STDP synapse allows it to be used in reinforcement learning tasks. This allows a network to learn which of the many cues and actions preceding a reward should be credited for the reward.

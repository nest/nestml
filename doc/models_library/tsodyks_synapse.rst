tsodyks_synapse
###############

Synapse type with short term plasticity

Description
+++++++++++

This synapse model implements synaptic short-term depression and short-term
facilitation according to [1]_. In particular it solves Eqs (3) and (4) from
this paper in an exact manner.

Synaptic depression is motivated by depletion of vesicles in the readily
releasable pool of synaptic vesicles (variable x in equation (3)). Synaptic
facilitation comes about by a presynaptic increase of release probability,
which is modeled by variable U in Eq (4).

The original interpretation of variable y is the amount of glutamate
concentration in the synaptic cleft. In [1]_ this variable is taken to be
directly proportional to the synaptic current caused in the postsynaptic
neuron (with the synaptic weight w as a proportionality constant). In order
to reproduce the results of [1]_ and to use this model of synaptic plasticity
in its original sense, the user therefore has to ensure the following
conditions:

1. The postsynaptic neuron must be of type ``iaf_psc_exp`` or similar,
   because these neuron models have a postsynaptic current which decays
   exponentially.

2. The time constant of each ``tsodyks_synapse`` targeting a particular neuron
   must be chosen equal to that neuron's synaptic time constant. In particular
   that means that all synapses targeting a particular neuron have the same
   parameter ``tau_psc``.

However, there are no technical restrictions using this model of synaptic
plasticity also in conjunction with neuron models that have a different
dynamics for their synaptic current or conductance. The effective synaptic
weight, which will be transmitted to the postsynaptic neuron upon occurrence
of a spike at time t is :math:`u(t) \cdot x(t) \cdot w`, where ``u(t)`` and ``x(t)``
are defined in Eq (3) and (4), w is the synaptic weight specified upon connection.
The interpretation is as follows: The quantity :math:`u(t) \cdot x(t)` is the release
probability times the amount of releasable synaptic vesicles at time t of the
presynaptic neuron's spike, so this equals the amount of transmitter expelled
into the synaptic cleft.

The amount of transmitter then relaxes back to 0 with time constant tau_psc
of the synapse's variable y. Since the dynamics of ``y(t)`` is linear, the
postsynaptic neuron can reconstruct from the amplitude of the synaptic
impulse :math:`u(t) \cdot x(t) \cdot w` the full shape of ``y(t)``. The postsynaptic
neuron, however, might choose to have a synaptic current that is not necessarily
identical to the concentration of transmitter ``y(t)`` in the synaptic cleft. It may
realize an arbitrary postsynaptic effect depending on ``y(t)``.

Please note that the initial value of ``u`` should be equal to the value of
``U``. Thus, when setting a new value for ``U`` before the start of the
simulation, make sure to set ``u`` to the same value.


References
++++++++++

.. [1] Tsodyks M, Uziel A, Markram H (2000). Synchrony generation in recurrent
       networks with frequency-dependent synapses. Journal of Neuroscience,
       20 RC50. URL: http://infoscience.epfl.ch/record/183402


Parameters
++++++++++


.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "d", "ms", "1ms", "Synaptic transmission delay"    
    "w", "real", "1", "Synaptic weight"    
    "tau_psc", "ms", "3ms", ""    
    "tau_fac", "ms", "0ms", "Setting tau_fac = 0 disables facilitation"    
    "tau_rec", "ms", "800ms", ""    
    "U", "real", ".5", ""    

        
        
State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "x", "real", "1", ""    
    "y", "real", "0", ""    
    "u", "real", "U", ""
    "t_last_update", "ms", "0ms", ""
    
    
    
Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `tsodyks_synapse <https://github.com/nest/nestml/tree/main/models/synapses/tsodyks_synapse.nestml>`_.



.. footer::

   Generated at 2026-03-19 12:51:11.498713

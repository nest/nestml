stdp_triplet_synapse
####################


stdp_triplet_synapse - Synapse type with triplet spike-timing dependent plasticity

Description
+++++++++++

A connection with spike time dependent plasticity accounting for spike triplet effects (as defined in [1]_).

Nearest-neighbour variant of pre- and postsynaptic spike coupling.

Traditional STDP models express the weight change as a function of pairs of pre- and postsynaptic spikes, but these fall short in accounting for the frequency dependence of weight changes. To improve the fit between model and empirical data, [4]_ propose a "triplet" rule, which considers sets of three spikes, that is, two pre and one post, or one pre and two post.

.. figure:: https://raw.githubusercontent.com/nest/nestml/main/doc/fig/stdp_triplet_synapse.png

   Figure 1 from [4]_.

Two traces, with different time constants, are defined for both pre- and postsynaptic partners. The temporal evolution of the traces is illustrated in panels B and C: for the all-to-all variant of the rule, each trace is incremented by 1 upon a spike (panel B), whereas for the nearest-neighbour variant, each trace is reset to 1 upon a spike (panel C). The weight updates are then computed as a function of the trace values and four coefficients: a depression pair term :math:`A_2^-` and triplet term :math:`A_3^-`, and a facilitation pair term :math:`A_2^+` and triplet term :math:`A_3^+`. A presynaptic spike after a postsynaptic one induces depression, if the temporal difference is not much larger than :math:`\tau_-` (pair term, :math:`A_2^-`). The presence of a previous presynaptic spike gives an additional contribution (2-pre-1-post triplet term, :math:`A_3^-`) if the interval between the two presynaptic spikes is not much larger than :math:`\tau_x`. Similarly, the triplet term for potentiation depends on one presynaptic spike but two postsynaptic spikes. The presynaptic spike must occur before the second postsynaptic one with a temporal difference not much larger than :math:`\tau_+`.

.. code-block:: nestml

   parameters:
       tau_plus ms = 16.8 ms    time constant for tr_r1
       tau_x ms = 101 ms        time constant for tr_r2
       tau_minus ms = 33.7 ms   time constant for tr_o1
       tau_y ms = 125 ms        time constant for tr_o2

   equations:
       kernel tr_r1_kernel = exp(-t / tau_plus)
       inline tr_r1 real = convolve(tr_r1_kernel, pre_spikes)

       kernel tr_r2_kernel = exp(-t / tau_x)
       inline tr_r2 real = convolve(tr_r2_kernel, pre_spikes)

       kernel tr_o1_kernel = exp(-t / tau_minus)
       inline tr_o1 real = convolve(tr_o1_kernel, post_spikes)

       kernel tr_o2_kernel = exp(-t / tau_y)
       inline tr_o2 real = convolve(tr_o2_kernel, post_spikes)

The weight update rules can then be expressed in terms of the traces and parameters, directly following the formulation in the paper (eqs. 3 and 4, [4]_):

.. code-block:: nestml

   parameters:
       A2_plus real = 7.5e-10
       A3_plus real = 9.3e-3
       A2_minus real = 7e-3
       A3_minus real = 2.3e-4

       Wmax real = 100.
       Wmin real = 0.

   onReceive(post_spikes):
        potentiate synapse
       w_ real = w + tr_r1 * (A2_plus + A3_plus * tr_o2)
       w = min(Wmax, w_)

   onReceive(pre_spikes):
        depress synapse
       w_ real = w  -  tr_o1 * (A2_minus + A3_minus * tr_r2)
       w = max(Wmin, w_)

       # deliver spike to postsynaptic partner
       emit_spike(w)

Note that in this particular STDP synapse model, the weight is not allowed to be negative. In case an inhibitory STDP synapse needs to be modeled, this model (with weight >= 0 at all times) can be connected to a postsynaptic neuron at its appropriate (inhibitory) input port. The sign of the postsynaptic response is thus handled in the postsynaptic neuron. In principle, an STDP synapse model can be defined that allows for negative weights, but in this case, care should be taken to prevent the sign of the weight from changing during learning, as a biological synapse cannot simply switch from one type to another, say, from glutamatergic to GABAergic.

.. note::

   See https://github.com/nest/nestml/issues/703 for a potential edge-case issue with this model.


References
++++++++++
.. [1] Pfister JP, Gerstner W (2006). Triplets of spikes in a model
       of spike timing-dependent plasticity. The Journal of Neuroscience
       26(38):9673-9682. DOI: https://doi.org/10.1523/JNEUROSCI.1425-06.2006



Parameters
++++++++++


.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto


    "tau_plus", "ms", "16.8 ms", "time constant for tr_r1"
    "tau_x", "ms", "101 ms", "time constant for tr_r2"
    "tau_minus", "ms", "33.7 ms", "time constant for tr_o1"
    "tau_y", "ms", "125 ms", "time constant for tr_o2"
    "A2_plus", "real", "7.5e-10", ""
    "A3_plus", "real", "0.0093", ""
    "A2_minus", "real", "0.007", ""
    "A3_minus", "real", "0.00023", ""
    "Wmax", "nS", "100 nS", ""
    "Wmin", "nS", "0 nS", ""


State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto


    "w", "nS", "1 nS", "Synaptic weight"
    "tr_r1", "real", "0.0", ""
    "tr_r2", "real", "0.0", ""
    "tr_o1", "real", "0.0", ""
    "tr_o2", "real", "0.0", ""
Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `stdp_triplet_synapse <https://github.com/nest/nestml/tree/main/models/synapses/stdp_triplet_synapse.nestml>`_.


.. include:: stdp_triplet_synapse_characterisation.rst


.. footer::

   Generated at 2026-09-07 17:58:04.409297

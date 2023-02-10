Modeling neurons in NESTML
==========================

.. figure:: https://raw.githubusercontent.com/clinssen/nestml/angela_illustrations/doc/fig/neuron_illustration.svg
   :width: 324px
   :height: 307px
   :align: right
   :target: #

Writing the NESTML model
########################

The top-level element of the model is ``neuron``, followed by a name. All other blocks appear inside of here.

.. code-block:: nestml

   neuron hodkin_huxley:
     # [...]
   end


Neuronal interactions
---------------------

Input
~~~~~

A neuron model written in NESTML can be configured to receive two distinct types of input: spikes and continuous-time values. This can be indicated using the following syntax:

.. code-block:: nestml

   input:
     I_stim pA <- continuous
     AMPA_spikes pA <- spike
   end

The general syntax is:

::

    port_name dataType <- inputQualifier* (spike | continuous)

For spiking input ports, the qualifier keywords decide whether inhibitory and excitatory inputs are lumped together into a single named input port, or if they are separated into differently named input ports based on their sign. When processing a spike event, some simulators (including NEST) use the sign of the amplitude (or weight) property in the spike event to indicate whether it should be considered an excitatory or inhibitory spike. By using the qualifier keywords, a single spike handler can route each incoming spike event to the correct input buffer (excitatory or inhibitory). Compare:

.. code-block:: nestml

   input:
     # [...]
     all_spikes pA <- spike
   end

In this case, all spike events will be processed through the ``all_spikes`` input port. A spike weight could be positive or negative, and the occurrences of ``all_spikes`` in the model should be considered a signed quantity.

.. code-block:: nestml

   input:
     # [...]
     AMPA_spikes pA <- excitatory spike
     GABA_spikes pA <- inhibitory spike
   end

In this case, spike events that have a negative weight are routed to the ``GABA_spikes`` input port, and those that have a positive weight to the ``AMPA_spikes`` port.

It is equivalent if either both `inhibitory` and `excitatory` are given, or neither: an unmarked port will by default handle all incoming presynaptic spikes.

.. list-table::
   :header-rows: 1
   :widths: 10 60

   * - Keyword
     - The incoming weight :math:`w`...
   * - none, or ``excitatory`` and ``inhibitory``
     - ... may be positive or negative. It is added to the buffer with signed value :math:`w` (positive or negative).
   * - ``excitatory``
     - ... should not be negative. It is added to the buffer with non-negative magnitude :math:`w`.
   * - ``inhibitory``
     - ... should be negative. It is added to the buffer with non-negative magnitude :math:`-w`.


Integrating current input
^^^^^^^^^^^^^^^^^^^^^^^^^

The current port symbol (here, `I_stim`) is available as a variable and can be used in expressions, e.g.:

.. code-block:: nestml

   equations
     V_m' = -V_m/tau_m + ... + I_stim
   end

   input:
     I_stim pA <- continuous
   end



Integrating spiking input
^^^^^^^^^^^^^^^^^^^^^^^^^

Spikes arriving at the input port of a neuron can be written as a spike train :math:`s(t)`:

.. math::

   \large s(t) = \sum_{i=1}^N \delta(t - t_i)

To model the effect that an arriving spike has on the state of the neuron, a convolution with a kernel can be used. The kernel defines the postsynaptic response kernel, for example, an alpha (bi-exponential) function, decaying exponential, or a delta function. (See :ref:`Kernel functions` for how to define a kernel.) The convolution of the kernel with the spike train is defined as follows:

.. math::

   \large (f \ast s)(t) = \sum_{i=1}^N w_i \cdot f(t - t_i)

where :math:`w_i` is the weight of spike :math:`i`.

For example, say there is a spiking input port defined named ``spikes``. A decaying exponential with time constant ``tau_syn`` is defined as postsynaptic kernel ``G``. Their convolution is expressed using the ``convolve(f, g)`` function, which takes a kernel and input port, respectively, as its arguments:

.. code-block:: nestml

   equations:
     kernel G = exp(-t/tau_syn)
     V_m' = -V_m/tau_m + convolve(G, spikes)
   end

The type of the convolution is equal to the type of the second parameter, that is, of the spike buffer. Kernels themselves are always untyped.


(Re)setting synaptic integration state
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When convolutions are used, additional state variables are required for each pair *(shape, spike input port)* that appears as the parameters in a convolution. These variables track the dynamical state of that kernel, for that input port. The number of variables created corresponds to the dimensionality of the kernel. For example, in the code block above, the one-dimensional kernel ``G`` is used in a convolution with spiking input port ``spikes``. During code generation, a new state variable called ``G__conv__spikes`` is created for this combination, by joining together the name of the kernel with the name of the spike buffer using (by default) the string “__conv__”. If the same kernel is used later in a convolution with another spiking input port, say ``spikes_GABA``, then the resulting generated variable would be called ``G__conv__spikes_GABA``, allowing independent synaptic integration between input ports but allowing the same kernel to be used more than once.

The process of generating extra state variables for keeping track of convolution state is normally hidden from the user. For some models, however, it might be required to set or reset the state of synaptic integration, which is stored in these internally generated variables. For example, we might want to set the synaptic current (and its rate of change) to 0 when firing a dendritic action potential. Although we would like to set the generated variable ``G__conv__spikes`` to 0 in the running example, a variable by this name is only generated during code generation, and does not exist in the namespace of the NESTML model to begin with. To still allow referring to this state in the context of the model, it is recommended to use an inline expression, with only a convolution on the right-hand side.

For example, suppose we define:

.. code-block:: nestml

   inline g_dend pA = convolve(G, spikes)

Then the name ``g_dend`` can be used as a target for assignment:

.. code-block:: nestml

   update:
     g_dend = 42 pA
   end

This also works for higher-order kernels, e.g. for the second-order alpha kernel :math:`H(t)`:

.. code-block:: nestml

   kernel H'' = (-2/tau_syn) * H' - 1/tau_syn**2) * H

We can define an inline expression with the same port as before, ``spikes``:

.. code-block:: nestml

   inline h_dend pA = convolve(H, spikes)

The name ``h_dend`` now acts as an alias for this particular convolution. We can now assign to the inline defined variable up to the order of the kernel:

.. code-block:: nestml

   update:
     h_dend = 42 pA
     h_dend' = 10 pA/ms
   end

For more information, see the :doc:`Active dendrite tutorial </tutorials/active_dendrite/nestml_active_dendrite_tutorial>`.


Multiple input ports
^^^^^^^^^^^^^^^^^^^^

If there is more than one line specifying a `spike` or `continuous` port with the same sign, a neuron with multiple receptor types is created. For example, say that we define three spiking input ports as follows:

.. code-block:: nestml

   input:
     spikes1 nS <- spike
     spikes2 nS <- spike
     spikes3 nS <- spike
   end

For the sake of keeping the example simple, we assign a decaying exponential-kernel postsynaptic response to each input port, each with a different time constant:

.. code-block:: nestml

   equations:
     kernel I_kernel1 = exp(-t / tau_syn1)
     kernel I_kernel2 = exp(-t / tau_syn2)
     kernel I_kernel3 = -exp(-t / tau_syn3)
     inline I_syn pA = convolve(I_kernel1, spikes1) - convolve(I_kernel2, spikes2) + convolve(I_kernel3, spikes3)
     V_m' = -(V_m - E_L) / tau_m + I_syn / C_m
   end


Multiple input ports with vectors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The input ports can also be defined as vectors. For example,

.. code-block:: nestml

   neuron multi_synapse_vectors:
       input:
         AMPA_spikes pA <- excitatory spike
         GABA_spikes pA <- inhibitory spike
         NMDA_spikes pA <- spike
         foo[2] pA <- spike
         exc_spikes[3] pA <- excitatory spike
         inh_spikes[3] pA <- inhibitory spike
       end
   end

In this example, the spiking input ports ``foo``, ``exc_spikes``, and ``inh_spikes`` are defined as vectors. The integer surrounded by ``[`` and ``]`` determines the size of the vector. The size of the input port must always be a positive-valued integer.


Output
~~~~~~

``emit_spike``: calling this function in the ``update`` block results in firing a spike to all target neurons and devices time stamped with the current simulation time.



Generating code
###############

Co-generation of neuron and synapse
-----------------------------------

The ``update`` block in a NESTML model is translated into the ``update`` method in NEST.

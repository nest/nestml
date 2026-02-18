Modeling neurons in NESTML
==========================

.. figure:: https://raw.githubusercontent.com/nest/nestml/master/doc/fig/neuron_illustration.svg
   :width: 324px
   :height: 307px
   :align: right
   :target: #

Writing the NESTML model
########################

The top-level element of the model is ``model``, followed by a name. All other blocks appear inside of here.

.. code-block:: nestml

   model hodkin_huxley_neuron:
       # [...]

Neuronal interactions
---------------------

Input
~~~~~

A neuron model written in NESTML can be configured to receive two distinct types of input: spikes and continuous-time values. This can be indicated using the following syntax:

.. code-block:: nestml

   input:
       AMPA_spikes <- spike
       I_stim pA <- continuous

The spiking input ports are declared without a data type, whereas the continuous input ports must have a data type.


Integrating current input
^^^^^^^^^^^^^^^^^^^^^^^^^

The current port symbol (here, ``I_stim``) is available as a variable and can be used in expressions, e.g.:

.. code-block:: nestml

   equations
       V_m' = -V_m / tau_m + ... + I_stim / C_m

   input:
       I_stim pA <- continuous


Integrating spiking input
^^^^^^^^^^^^^^^^^^^^^^^^^

To model the effect that an arriving spike has on the state of the neuron, a convolution with a kernel can be used. The kernel defines the postsynaptic response kernel, for example, an alpha (bi-exponential) function, decaying exponential, or a delta function. (See :ref:`Kernel functions` for how to define a kernel.) The convolution of the kernel with the spike train is defined as follows:

.. math::

   \begin{align*}
   \large (f \ast s)(t) &= \int s(u) f(t-u) du \\
                        &= \sum_{i=1}^N \int w_i \cdot \delta(u-t_i) f(t-u) du \\
                        &= \sum_{i=1}^N w_i \cdot f(t - t_i)
   \end{align*}

For example, say there is a spiking input port defined named ``spike_in_port``, which receives weighted spike events:

.. code-block:: nestml

   input:
       spike_in_port <- spike

A decaying exponential with time constant ``tau_syn`` is defined as postsynaptic kernel ``G``. Their convolution is expressed using the ``convolve()`` function, which takes a kernel and input port, respectively, as its arguments:

.. code-block:: nestml

   equations:
       kernel G = exp(-t / tau_syn)
       inline I_syn pA = convolve(G, spike_in_port)

The incoming spikes could have been equivalently handled with an ``onReceive`` event handler block:

.. code-block:: nestml

   state:
       I_syn pA = 0 pA

   equations:
       I_syn' = -I_syn / tau_syn

   onReceive(spike_in_port):
       I_syn += sift(spike_in_port, t)
Multiple input ports
^^^^^^^^^^^^^^^^^^^^

If there is more than one line specifying a `spike` or `continuous` port with the same sign, a neuron with multiple receptor types is created. For example, say that we define three spiking input ports and two continuous currents as follows:

.. code-block:: nestml

   input:
       spike_in_port1 <- spike
       spike_in_port2 <- spike
       spike_in_port3 <- spike
       I_stim1 <- continuous
       I_stim2 <- continuous

For the sake of keeping the example simple, we assign a decaying exponential-kernel postsynaptic response to each spiking input port, each with a different time constant and the continuous currents are added to, say, the membrane potential of the soma (``V_m``) and the distal (``V_d``) parts of the neuron:

.. code-block:: nestml

   equations:
       kernel I_kernel1 = exp(-t / tau_syn1)
       kernel I_kernel2 = exp(-t / tau_syn2)
       kernel I_kernel3 = -exp(-t / tau_syn3)
       inline I_syn pA = unit_psc * (convolve(I_kernel1, spike_in_port1) - convolve(I_kernel2, spike_in_port2) + convolve(I_kernel3, spike_in_port3))
       V_m' = -(V_m - E_L) / tau_m + (I_syn + I_stim1) / C_m
       V_d' = -(V_d - E_L) / tau_d + I_stim2 / C_m


Multiple input ports with vectors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The input ports can also be defined as vectors. For example,

.. code-block:: nestml

   neuron multi_synapse_vectors:
       input:
           AMPA_spikes <- spike
           GABA_spikes <- spike
           NMDA_spikes <- spike
           foo[2] <- spike
           exc_spikes[3] <- spike
           inh_spikes[3] <- spike

       equations:
           kernel I_kernel_exc = exp(-t / tau_syn_exc)
           kernel I_kernel_inh = exp(-t / tau_syn_inh)
           inline I_syn_exc pA = convolve(I_kernel_exc, exc_spikes[1]) * pA
           inline I_syn_inh pA = convolve(I_kernel_inh, inh_spikes[1]) * pA


In this example, the spiking input ports ``foo``, ``exc_spikes``, and ``inh_spikes`` are defined as vectors. The integer surrounded by ``[`` and ``]`` determines the size of the vector. The size of the input port must always be a positive-valued integer.

They could also be used in differential equations defined in the ``equations`` block as shown for ``exc_spikes[1]`` and ``inh_spikes[1]`` in the example above.


Output
~~~~~~

``emit_spike``: calling this function in the ``update`` block results in firing a spike to all target neurons and devices time stamped with the current simulation time.


Implementing refractoriness
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to model an absolute refractory state, in which the neuron cannot fire action potentials, different approaches can be used. In general, an extra parameter (say, ``refr_T``) is introduced, that defines the duration of the refractory period. A new state variable (say, ``refr_t``) can then act as a timer, counting the time of the refractory period that has already elapsed. The dynamics of ``refr_t`` could be specified in the ``update`` block, as follows:

.. code-block:: nestml

   update:
       refr_t -= resolution()

The test for refractoriness can then be added in the ``onCondition`` block as follows:

.. code-block:: nestml

   # if not refractory and threshold is crossed...
   onCondition(refr_t <= 0 ms and V_m > V_th):
       V_m = E_L    # Reset the membrane potential
       refr_t = refr_T    # Start the refractoriness timer
       emit_spike()

The disadvantage of this method is that it requires a call to the ``resolution()`` function, which is only supported by fixed-timestep simulators. To write the model in a more generic way, the refractoriness timer can alternatively be expressed as an ODE:

.. code-block:: nestml

   equations:
       refr_t' = -1 / s    # a timer counting back down to zero

Typically, the membrane potential should remain clamped to the reset or leak potential during the refractory period. It depends on the intended behavior of the model whether the synaptic currents and conductances also continue to be integrated or whether they are reset, and whether incoming spikes during the refractory period are taken into account or ignored.

In order to hold the membrane potential at the reset voltage during refractoriness, it can be simply excluded from the integration call:

.. code-block:: nestml

   equations:
       I_syn' = ...
       V_m' = ...
       refr_t' = -1 / s    # Count down towards zero

   update:
       if refr_t > 0 ms:
           # neuron is absolute refractory, do not evolve V_m
           integrate_odes(I_syn, refr_t)
       else:
           # neuron not refractory
           integrate_odes(I_syn, V_m)

Note that in some cases, the finite resolution by which real numbers are expressed (as floating point numbers) in computers, can cause unexpected behaviors. If the simulation resolution is not exactly representable as a float (say, :math:`\Delta t` = 0.1 ms) then it could be the case that after 20 simulation steps, the timer has not reached zero, but a very small value very close to zero (say, 0.00000001 ms), causing the refractory period to end only in the next timestep. If this kind of behavior is undesired, the simulation resolution and refractory period can be chosen as powers of two (which can be represented exactly as floating points), or a small "epsilon" value can be included in the comparison in the model:

.. code-block:: nestml

   parameters:
       float_epsilon ms = 1E-9 ms

   onCondition(refr_t <= float_epsilon ...):
       # ...

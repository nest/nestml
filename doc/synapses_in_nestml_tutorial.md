Modeling synapses in NESTML
===========================

A synapse is a special component in NESTML, because some simulators (notably, NEST) treat connections (edges) fundamentally differently from neurons (nodes).

The behaviour of a synapse is fundamentally determined by two blocks, `preReceive` and `postReceive`, and the `deliver_spike(w, d)` function.


preReceive
----------

The statements in this block will be triggered when a presynaptic spike arrives. These usually include a single call to `deliver_spike()` (but may include zero or more, e.g. in the case of an unreliable synapse or due to if..then..else statements).


postReceive
-----------

The statements in this block will be triggered when a postSynaptic spike arrives. This is useful, for example, for potentiating a synapse due to a "post-after-pre" spike pairing.

Note that in the NEST target, the statements in this block will only be run at the end of each communication interval, when iterating the postsynaptic spikes buffer.



deliver_spike(w, d) function
----------------------------

After a spike has been received in the `preReceive` block, the weight (and delay) of the neuron are, potentially, updated. The spike then needs to be passed on to the postsynaptic partner. This can be done by calling the `deliver_spike` function with the appropriate (new) weight and delay.

@nest:: namespace magic keywords.



Magic keyword attributes
------------------------

@homogeneous, @heterogeneous (default)

Example:

	synapse xyz:

	  parameters:
	    w nS = 900 pS  @nest::weight @homogeneous
	    d ms = .9 ms  @nest::delay @heterogeneous
	    foo ms = 42 ms  @homogeneous
	    bar pF = 100. pF  @heterogeneous
	  end

	  preReceive:
	    deliver_spike(w, d)
	  end

	end






The NEST target
---------------

NEST target synapses are not allowed to have any internal dynamics (ODEs). This is due to the fact that synapses are, unlike nodes, not updated on a regular time grid.

Additionally, NEST stores and updates the postsynaptic trace in the postsynaptic node class. This means that the shape of the postsynaptic trace is restricted to those supported in NEST, and that parameters (such as the decay time constant of the trace) have to be set by hand on the postsynaptic object. At the time of writing, only exponentially decaying traces, that are incremented by 1 at the time of a spike, are supported.


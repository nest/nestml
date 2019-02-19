Modeling synapses in NESTML
===========================

A synapse is a special component in NESTML, because some simulators (notably, NEST) treat connections (edges) fundamentally differently from neurons (nodes).

The behaviour of a synapse is fundamentally determined by the `preReceive` block and the `deliver_spike(w, d)` function.


preReceive
----------

The statements in this block will be triggered when a presynaptic spike arrives. These usually include a single call to `deliver_spike()` (but may include zero or more, e.g. in the case of an unreliable synapse or due to if..then..else statements).


deliver_spike(w, d) function
----------------------------

After a spike has been received in the `preReceive` block, the weight (and delay) of the neuron are, potentially, updated. The spike then needs to be passed on to the postsynaptic partner. This can be done by calling the `deliver_spike` function with the appropriate (new) weight and delay.


Link to the simulator namespace
-------------------------------

When generating code, simulators such as NEST need to have a unique internal reference for the parameters that pass through the API involved with sending a spike, namely, the weight and delay of the connection. For this purpose, decorator keywords such as `@nest::weight` exist, which can be used to mark a parameter (which might have a name such as `w` or `wght`) as uniquely corresponding to the NEST namespace name `weight`. Example:

			
	synapse static:

		parameters:
			w nS = 900 pS   @nest::weight
			d ms = .9 ms    @nest::delay
		end

		[...]

	end



Sharing parameters between synapses
-----------------------------------

If one or more synapse parameters are the same across a population (homogeneous), then sharing the parameter value can save vast amounts of memory. To mark a particular parameter as homogeneous, use the `@homogeneous` decorator keyword. This can be done on a per-parameter basis. By default, parameters are heterogeneous and can be set on a per-synapse basis by the user. Example:

	synapse static:

		parameters:
			a nS = 10 pS   @nest::accumulator
			b ms = 10 ms   @nest::beta_Ca
		end

		[...]

	end




The NEST target
---------------

NEST target synapses are not allowed to have any internal dynamics (ODEs). This is due to the fact that synapses are, unlike nodes, not updated on a regular time grid.

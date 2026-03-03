ignore_and_fire_neuron
######################

ignore_and_fire - Neuron generating spikes at fixed intervals irrespective of inputs


Description
+++++++++++

The ``ignore_and_fire`` neuron is a neuron model generating spikes at a predefined ``firing_rate`` with a constant inter-spike interval ("fire"), irrespective of its inputs ("ignore"). In this simplest version of the ``ignore_and_fire`` neuron, the inputs from other neurons or devices are not processed at all (*). The ``ignore_and_fire`` neuron is primarily used for neuronal-network model verification and validation purposes, in particular, to evaluate the correctness and performance of connectivity generation and inter-neuron communication. It permits an easy scaling of the network size and/or connectivity without affecting the output spike statistics. The amount of network traffic is predefined by the user, and therefore fully controllable and predictable, irrespective of the network size and structure.

To create asynchronous activity for a population of ``ignore_and_fire`` neurons, the firing ``phase``s can be randomly initialised. Note that the firing ``phase`` is a real number, defined as the time to the next spike relative to the firing period.

The model can easily be extended and equipped with any arbitrary input processing (such as calculating input currents with alpha-function shaped PSC kernels or updating the gating variables in the Hodgkin-Huxley model) or (after-) spike generation dynamics to make it more similar and comparable to other non-ignorant neuron models. In such extended ignore_and_fire models, the spike emission process would still be decoupled from the intrinsic neuron dynamics.

.. note::

   This neuron model can only be used in combination with a fixed
   simulation resolution (timestep size).

Authors
+++++++

Tetzlaff (February 2021; January 2022)

Copyright statement
+++++++++++++++++++

This file is part of NEST.

Copyright (C) 2004 The NEST Initiative

NEST is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

NEST is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with NEST.  If not, see <http://www.gnu.org/licenses/>.


Parameters
++++++++++
.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "firing_rate", "Bq", "10.0Bq", "firing rate"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "phase", "real", "1.0", "relative time to next spike (in (0,1])"    
    "phase_steps", "integer", "firing_period_steps / 2", "start halfway through the interval by default"




Equations
+++++++++





Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `ignore_and_fire_neuron <https://github.com/nest/nestml/tree/master/models/neurons/ignore_and_fire_neuron.nestml>`_.

.. include:: ignore_and_fire_neuron_characterisation.rst


.. footer::

   Generated at 2026-02-04 14:40:55.511851
izhikevich_neuron
#################

izhikevich - Izhikevich neuron model


Description
+++++++++++

Implementation of the simple spiking neuron model introduced by Izhikevich [1]_. The dynamics are given by:

.. math::

   dV_{m}/dt &= 0.04 V_{m}^2 + 5 V_{m} + 140 - U_{m} + I\\
   dU_{m}/dt &= a (b V_{m} - U_{m})

.. math::

   &\text{if}\;\; V_{m} \geq V_{th}:\\
   &\;\;\;\; V_{m} \text{ is set to } c\\
   &\;\;\;\; U_{m} \text{ is incremented by } d\\
   & \, \\
   &V_{m} \text{ jumps on each spike arrival by the weight of the spike}

Incoming spikes cause an instantaneous jump in the membrane potential proportional to the strength of the synapse.

As published in [1]_, the numerics differs from the standard forward Euler technique in two ways:

1) the new value of :math:`U_{m}` is calculated based on the new value of :math:`V_{m}`, rather than the previous value
2) the variable :math:`V_{m}` is updated using a time step half the size of that used to update variable :math:`U_{m}`.

This model will instead be simulated using the numerical solver that is recommended by ODE-toolbox during code generation.

References
++++++++++

.. [1] Izhikevich, Simple Model of Spiking Neurons, IEEE Transactions on Neural Networks (2003) 14:1569-1572

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

    
    "a", "real", "0.02", "describes time scale of recovery variable"    
    "b", "real", "0.2", "sensitivity of recovery variable"    
    "c", "mV", "-65mV", "after-spike reset value of V_m"    
    "d", "real", "8.0", "after-spike reset value of U_m"    
    "V_m_init", "mV", "-65mV", "initial membrane potential"    
    "V_min", "mV", "-inf * mV", "Absolute lower value for the membrane potential."    
    "V_th", "mV", "30mV", "Threshold potential"    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "V_m_init", "Membrane potential"    
    "U_m", "real", "b * V_m_init", "Membrane potential recovery variable"




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\frac{ 0.04 \cdot V_{m} \cdot V_{m} } { \mathrm{mV} } + 5.0 \cdot V_{m} + (140 - U_{m}) \cdot \mathrm{mV} + ((I_{e} + I_{stim}) \cdot \mathrm{GOhm})) } \right) 

.. math::
   \frac{ dU_{m} } { dt }= \frac{ a \cdot (b \cdot V_{m} - U_{m} \cdot \mathrm{mV}) } { (\mathrm{mV} \cdot \mathrm{ms}) }



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `izhikevich_neuron <https://github.com/nest/nestml/tree/master/models/neurons/izhikevich_neuron.nestml>`_.

.. include:: izhikevich_neuron_characterisation.rst


.. footer::

   Generated at 2026-02-04 14:40:55.675859
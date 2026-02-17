izhikevich_psc_alpha_neuron
###########################

izhikevich_psc_alpha - Detailed Izhikevich neuron model with alpha-kernel post-synaptic current


Description
+++++++++++

Implementation of the simple spiking neuron model introduced by Izhikevich [1]_, with membrane potential in (milli)volt
and current-based synapses.

The dynamics are given by:

.. math::

   C_m \frac{dV_m}{dt} = k (V - V_t)(V - V_t) - u + I + I_{syn,ex} + I_{syn,in}
   \frac{dU_m}{dt} = a(b(V_m - E_L) - U_m)

   &\text{if}\;\;\; V_m \geq V_{th}:\\
   &\;\;\;\; V_m \text{ is set to } c
   &\;\;\;\; U_m \text{ is incremented by } d

On each spike arrival, the membrane potential is subject to an alpha-kernel current of the form:

.. math::

   I_syn = I_0 \cdot t \cdot \exp\left(-t/\tau_{syn}\right) / \tau_{syn}

See also
++++++++

izhikevich, iaf_psc_alpha


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

    
    "C_m", "pF", "200pF", "Membrane capacitance"    
    "k", "pF / (mV ms)", "8pF / mV / ms", "Spiking slope"    
    "V_r", "mV", "-65mV", "Resting potential"    
    "V_t", "mV", "-45mV", "Threshold potential"    
    "a", "1 / ms", "0.01 / ms", "Time scale of recovery variable"    
    "b", "nS", "9nS", "Sensitivity of recovery variable"    
    "c", "mV", "-65mV", "After-spike reset value of V_m"    
    "d", "pA", "60pA", "After-spike reset value of U_m"    
    "V_peak", "mV", "0mV", "Spike detection threshold (reset condition)"    
    "tau_syn_exc", "ms", "0.2ms", "Synaptic time constant of excitatory synapse"    
    "tau_syn_inh", "ms", "2ms", "Synaptic time constant of inhibitory synapse"    
    "refr_T", "ms", "2ms", "Duration of refractory period"    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "-65mV", "Membrane potential"    
    "U_m", "pA", "0pA", "Membrane potential recovery variable"    
    "refr_t", "ms", "0ms", "Refractory period timer"




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (k \cdot (V_{m} - V_{r}) \cdot (V_{m} - V_{t}) - U_{m} + I_{e} + I_{stim} + I_{syn,exc} - I_{syn,inh}) } \right) 

.. math::
   \frac{ dU_{m} } { dt }= a \cdot (b \cdot (V_{m} - V_{r}) - U_{m})

.. math::
   \frac{ drefr_{t} } { dt }= \frac{ -1000.0 \cdot \mathrm{ms} } { \mathrm{s} }



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `izhikevich_psc_alpha_neuron <https://github.com/nest/nestml/tree/master/models/neurons/izhikevich_psc_alpha_neuron.nestml>`_.

.. include:: izhikevich_psc_alpha_neuron_characterisation.rst


.. footer::

   Generated at 2026-02-04 14:40:55.104229
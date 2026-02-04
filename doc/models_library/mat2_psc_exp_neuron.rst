mat2_psc_exp_neuron
###################

mat2_psc_exp - Non-resetting leaky integrate-and-fire neuron model with exponential PSCs and adaptive threshold


Description
+++++++++++

mat2_psc_exp is an implementation of a leaky integrate-and-fire model
with exponential-kernel postsynaptic currents (PSCs). Thus, postsynaptic
currents have an infinitely short rise time.

The threshold is lifted when the neuron is fired and then decreases in a
fixed time scale toward a fixed level [3]_.

The threshold crossing is followed by a total refractory period
during which the neuron is not allowed to fire, even if the membrane
potential exceeds the threshold. The membrane potential is NOT reset,
but continuously integrated.

.. note::

   If tau_m is very close to tau_syn_exc or tau_syn_inh, numerical problems
   may arise due to singularities in the propagator matrics. If this is
   the case, replace equal-valued parameters by a single parameter.

   For details, please see ``IAF_neurons_singularity.ipynb`` in
   the NEST source code (``docs/model_details``).

References
++++++++++

.. [1] Rotter S and Diesmann M (1999). Exact simulation of
       time-invariant linear systems with applications to neuronal
       modeling. Biologial Cybernetics 81:381-402.
       DOI: https://doi.org/10.1007/s004220050570

.. [2] Diesmann M, Gewaltig M-O, Rotter S, Aertsen A (2001). State
       space analysis of synchronous spiking in cortical neural
       networks. Neurocomputing 38-40:565-571.
       DOI:https://doi.org/10.1016/S0925-2312(01)00409-X

.. [3] Kobayashi R, Tsubo Y and Shinomoto S (2009). Made-to-order
       spiking neuron model equipped with a multi-timescale adaptive
       threshold. Frontiers in Computuational Neuroscience 3:9.
       DOI: https://doi.org/10.3389/neuro.10.009.2009

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

    
    "tau_m", "ms", "5ms", "Membrane time constant"    
    "C_m", "pF", "100pF", "Capacitance of the membrane"    
    "refr_T", "ms", "2ms", "Duration of refractory period"    
    "E_L", "mV", "-70mV", "Resting potential"    
    "tau_syn_exc", "ms", "1ms", "Time constant of postsynaptic excitatory currents"    
    "tau_syn_inh", "ms", "3ms", "Time constant of postsynaptic inhibitory currents"    
    "tau_1", "ms", "10ms", "Short time constant of adaptive threshold"    
    "tau_2", "ms", "200ms", "Long time constant of adaptive threshold"    
    "alpha_1", "mV", "37mV", "Amplitude of short time threshold adaption [3]"    
    "alpha_2", "mV", "2mV", "Amplitude of long time threshold adaption [3]"    
    "omega", "mV", "19mV", "Resting spike threshold (absolute value, not relative to E_L)"    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_th_alpha_1", "mV", "0mV", "Two-timescale adaptive threshold"    
    "V_th_alpha_2", "mV", "0mV", "Two-timescale adaptive threshold"    
    "V_m", "mV", "E_L", "Absolute membrane potential"    
    "refr_t", "ms", "0ms", "Refractory period timer"




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac{ -(V_{m} - E_{L}) } { \tau_{m} } + \frac 1 { C_{m} } \left( { (I_{syn} + I_{e} + I_{stim}) } \right) 

.. math::
   \frac{ drefr_{t} } { dt }= \frac{ -1000.0 \cdot \mathrm{ms} } { \mathrm{s} }



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `mat2_psc_exp_neuron <https://github.com/nest/nestml/tree/master/models/neurons/mat2_psc_exp_neuron.nestml>`_.

.. include:: mat2_psc_exp_neuron_characterisation.rst


.. footer::

   Generated at 2026-02-04 14:40:55.843083
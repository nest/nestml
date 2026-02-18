iaf_psc_delta_fixed_timestep_neuron
###################################

iaf_psc_delta_fixed_timestep - Current-based leaky integrate-and-fire neuron model with delta-kernel post-synaptic currents


Description
+++++++++++

An implementation of a leaky integrate-and-fire model where the potential jumps on each spike arrival. The threshold crossing is followed by an absolute refractory period during which the membrane potential is clamped to the resting potential. Spikes arriving while the neuron is refractory are discarded.

The general framework for the consistent formulation of systems with neuron-like dynamics interacting by point events is described in [1]_.  A flow chart can be found in [2]_.

This model differs from ``iaf_psc_delta`` in that it assumes a fixed-timestep simulator, so the functions ``resolution()`` and ``steps()`` can be used.


References
++++++++++

.. [1] Rotter S, Diesmann M (1999). Exact simulation of
       time-invariant linear systems with applications to neuronal
       modeling. Biologial Cybernetics 81:381-402.
       DOI: https://doi.org/10.1007/s004220050570
.. [2] Diesmann M, Gewaltig M-O, Rotter S, & Aertsen A (2001). State
       space analysis of synchronous spiking in cortical neural
       networks. Neurocomputing 38-40:565-571.
       DOI: https://doi.org/10.1016/S0925-2312(01)00409-X


See also
++++++++

iaf_psc_alpha, iaf_psc_exp

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

    
    "tau_m", "ms", "10ms", "Membrane time constant"    
    "C_m", "pF", "250pF", "Capacity of the membrane"    
    "refr_T", "ms", "2ms", "Duration of refractory period"    
    "E_L", "mV", "-70mV", "Resting membrane potential"    
    "V_reset", "mV", "-70mV", "Reset potential of the membrane"    
    "V_th", "mV", "-55mV", "Spike threshold"    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "E_L", "Membrane potential"    
    "refr_counter", "integer", "0", "Refractory period timer"




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac{ -(V_{m} - E_{L}) } { \tau_{m} } + \frac 1 { C_{m} } \left( { (I_{e} + I_{stim}) } \right) 



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `iaf_psc_delta_fixed_timestep_neuron <https://github.com/nest/nestml/tree/master/models/neurons/iaf_psc_delta_fixed_timestep_neuron.nestml>`_.

.. include:: iaf_psc_delta_fixed_timestep_neuron_characterisation.rst


.. footer::

   Generated at 2026-02-04 14:40:55.700875
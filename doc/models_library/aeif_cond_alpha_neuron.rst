aeif_cond_alpha_neuron
######################

aeif_cond_alpha - Conductance based exponential integrate-and-fire neuron model


Description
+++++++++++

aeif_cond_alpha is the adaptive exponential integrate and fire neuron according to Brette and Gerstner (2005), with post-synaptic conductances in the form of a bi-exponential ("alpha") function.

The membrane potential is given by the following differential equation:

.. math::

   C_m \frac{dV_m}{dt} =
   -g_L(V_m-E_L)+g_L\Delta_T\exp\left(\frac{V_m-V_{th}}{\Delta_T}\right) -
   g_e(t)(V_m-E_e) \\
   -g_i(t)(V_m-E_i)-w + I_e

and

.. math::

   \tau_w \frac{dw}{dt} = a(V_m-E_L) - w

Note that the membrane potential can diverge to positive infinity due to the exponential term. To avoid numerical instabilities, instead of :math:`V_m`, the value :math:`\min(V_m,V_{peak})` is used in the dynamical equations.

.. note::

   The default refractory period for ``aeif`` models is zero, consistent with the model definition in
   Brette & Gerstner [1]_.  Thus, an ``aeif`` neuron with default parameters can fire multiple spikes in a single
   time step, which can lead to exploding spike numbers and extreme slow-down of simulations.
   To avoid such unphysiological behavior, you should set a refractory time ``refr_t > 0``.

References
++++++++++

.. [1] Brette R and Gerstner W (2005). Adaptive exponential
       integrate-and-fire model as an effective description of neuronal
       activity. Journal of Neurophysiology. 943637-3642
       DOI: https://doi.org/10.1152/jn.00686.2005

See also
++++++++

iaf_cond_alpha, aeif_cond_exp

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

    
    "C_m", "pF", "281.0pF", "Membrane capacitance"    
    "refr_T", "ms", "2ms", "Duration of refractory period"    
    "V_reset", "mV", "-60.0mV", "Reset potential"    
    "g_L", "nS", "30.0nS", "Leak conductance"    
    "E_L", "mV", "-70.6mV", "Leak reversal potential (a.k.a. resting potential)"    
    "a", "nS", "4nS", "Subthreshold adaptation"    
    "b", "pA", "80.5pA", "Spike-triggered adaptation"    
    "Delta_T", "mV", "2.0mV", "Slope factor"    
    "tau_w", "ms", "144.0ms", "Adaptation time constant"    
    "V_th", "mV", "-50.4mV", "Spike initiation threshold"    
    "V_peak", "mV", "0mV", "Spike detection threshold"    
    "E_exc", "mV", "0mV", "Excitatory reversal potential"    
    "tau_syn_exc", "ms", "0.2ms", "Synaptic time constant excitatory synapse"    
    "E_inh", "mV", "-85.0mV", "Inhibitory reversal potential"    
    "tau_syn_inh", "ms", "2.0ms", "Synaptic time constant for inhibitory synapse"    
    "I_e", "pA", "0pA", "Constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "E_L", "Membrane potential"    
    "w", "pA", "0pA", "Spike-adaptation current"    
    "refr_t", "ms", "0ms", "Refractory period timer"




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-g_{L} \cdot (V_{bounded} - E_{L}) + I_{spike} - I_{syn,exc} - I_{syn,inh} - w + I_{e} + I_{stim}) } \right) 

.. math::
   \frac{ dw } { dt }= \frac 1 { \tau_{w} } \left( { (a \cdot (V_{bounded} - E_{L}) - w) } \right) 

.. math::
   \frac{ drefr_{t} } { dt }= \frac{ -1000.0 \cdot \mathrm{ms} } { \mathrm{s} }



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `aeif_cond_alpha_neuron <https://github.com/nest/nestml/tree/master/models/neurons/aeif_cond_alpha_neuron.nestml>`_.

.. include:: aeif_cond_alpha_neuron_characterisation.rst


.. footer::

   Generated at 2026-02-04 14:40:55.297935
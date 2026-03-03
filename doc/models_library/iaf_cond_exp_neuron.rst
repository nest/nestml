iaf_cond_exp_neuron
###################

iaf_cond_exp - Simple conductance based leaky integrate-and-fire neuron model


Description
+++++++++++

iaf_cond_exp is an implementation of a spiking neuron using IAF dynamics with
conductance-based synapses. Incoming spike events induce a post-synaptic change
of conductance modelled by an exponential function. The exponential function
is normalised such that an event of weight 1.0 results in a peak conductance of
1 nS.

References
++++++++++

.. [1] Meffin H, Burkitt AN, Grayden DB (2004). An analytical
       model for the large, fluctuating synaptic conductance state typical of
       neocortical neurons in vivo. Journal of Computational Neuroscience,
       16:159-175.
       DOI: https://doi.org/10.1023/B:JCNS.0000014108.03012.81

See also
++++++++

iaf_psc_delta, iaf_psc_exp, iaf_cond_exp

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

    
    "C_m", "pF", "250pF", "Membrane capacitance"    
    "g_L", "nS", "16.6667nS", "Leak conductance"    
    "E_L", "mV", "-70mV", "Leak reversal potential (a.k.a. resting potential)"    
    "refr_T", "ms", "2ms", "Duration of refractory period"    
    "V_th", "mV", "-55mV", "Spike threshold potential"    
    "V_reset", "mV", "-60mV", "Reset potential"    
    "E_exc", "mV", "0mV", "Excitatory reversal potential"    
    "E_inh", "mV", "-85mV", "Inhibitory reversal potential"    
    "tau_syn_exc", "ms", "0.2ms", "Synaptic time constant of excitatory synapse"    
    "tau_syn_inh", "ms", "2ms", "Synaptic time constant of inhibitory synapse"    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "E_L", "Membrane potential"    
    "refr_t", "ms", "0ms", "Refractory period timer"




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-I_{leak} - I_{syn,exc} - I_{syn,inh} + I_{e} + I_{stim}) } \right) 

.. math::
   \frac{ drefr_{t} } { dt }= \frac{ -1000.0 \cdot \mathrm{ms} } { \mathrm{s} }



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `iaf_cond_exp_neuron <https://github.com/nest/nestml/tree/master/models/neurons/iaf_cond_exp_neuron.nestml>`_.

.. include:: iaf_cond_exp_neuron_characterisation.rst


.. footer::

   Generated at 2026-02-04 14:40:55.087771
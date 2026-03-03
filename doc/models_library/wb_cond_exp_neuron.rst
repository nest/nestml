wb_cond_exp_neuron
##################

wb_cond_exp - Wang-Buzsaki model


Description
+++++++++++

wb_cond_exp is an implementation of a modified Hodkin-Huxley model.

(1) Post-synaptic currents: Incoming spike events induce a post-synaptic change
of conductance modeled by an exponential function.

(2) Spike Detection: Spike detection is done by a combined threshold-and-local-
maximum search: if there is a local maximum above a certain threshold of
the membrane potential, it is considered a spike.

References
++++++++++

.. [1] Wang, X.J. and Buzsaki, G., (1996) Gamma oscillation by synaptic
       inhibition in a hippocampal interneuronal network model. Journal of
       neuroscience, 16(20), pp.6402-6413.

See Also
++++++++

hh_cond_exp_traub, wb_cond_multisyn

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

    
    "C_m", "pF", "100pF", "Membrane capacitance"    
    "g_Na", "nS", "3500nS", "Sodium peak conductance"    
    "g_K", "nS", "900nS", "Potassium peak conductance"    
    "g_L", "nS", "10nS", "Leak conductance"    
    "E_Na", "mV", "55mV", "Sodium reversal potential"    
    "E_K", "mV", "-90mV", "Potassium reversal potential"    
    "E_L", "mV", "-65mV", "Leak reversal potential (a.k.a. resting potential)"    
    "V_Tr", "mV", "-55mV", "Spike threshold"    
    "refr_T", "ms", "2ms", "Duration of refractory period"    
    "tau_syn_exc", "ms", "0.2ms", "Rise time of the excitatory synaptic alpha function"    
    "tau_syn_inh", "ms", "10ms", "Rise time of the inhibitory synaptic alpha function"    
    "E_exc", "mV", "0mV", "Excitatory synaptic reversal potential"    
    "E_inh", "mV", "-75mV", "Inhibitory synaptic reversal potential"    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "E_L", "Membrane potential"    
    "V_m_old", "mV", "E_L", "Membrane potential at previous timestep for threshold check"    
    "refr_t", "ms", "0ms", "Refractory period timer"    
    "Inact_h", "real", "alpha_h_init / (alpha_h_init + beta_h_init)", ""    
    "Act_n", "real", "alpha_n_init / (alpha_n_init + beta_n_init)", ""




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-(I_{Na} + I_{K} + I_{L}) + I_{e} + I_{stim} + I_{syn,exc} - I_{syn,inh}) } \right) 

.. math::
   \frac{ dAct_{n} } { dt }= (\text{alpha_n}(V_{m}) \cdot (1 - Act_{n}) - \text{beta_n}(V_{m}) \cdot Act_{n})

.. math::
   \frac{ dInact_{h} } { dt }= (\text{alpha_h}(V_{m}) \cdot (1 - Inact_{h}) - \text{beta_h}(V_{m}) \cdot Inact_{h})

.. math::
   \frac{ drefr_{t} } { dt }= \frac{ -1000.0 \cdot \mathrm{ms} } { \mathrm{s} }



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `wb_cond_exp_neuron <https://github.com/nest/nestml/tree/master/models/neurons/wb_cond_exp_neuron.nestml>`_.

.. include:: wb_cond_exp_neuron_characterisation.rst


.. footer::

   Generated at 2026-02-04 14:40:55.643617
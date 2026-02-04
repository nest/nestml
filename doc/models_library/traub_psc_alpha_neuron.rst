traub_psc_alpha_neuron
######################

traub_psc_alpha - Traub model according to Borgers 2017


Reduced Traub-Miles Model of a Pyramidal Neuron in Rat Hippocampus [1]_. Parameters obtained from reference [2]_.

Incoming spike events induce a post-synaptic change of current, modelled by an alpha function.

References
++++++++++

.. [1] R. D. Traub and R. Miles, Neuronal Networks of the Hippocampus,Cam- bridge University Press, Cambridge, UK, 1991.
.. [2] Borgers, C., 2017. An introduction to modeling neuronal dynamics (Vol. 66). Cham: Springer.

See also
++++++++

hh_cond_exp_traub

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

    
    "V_m_init", "mV", "-70mV", "Initial membrane potential"    
    "C_m", "pF", "100pF", "Membrane capacitance"    
    "g_Na", "nS", "10000nS", "Sodium peak conductance"    
    "g_K", "nS", "8000nS", "Potassium peak conductance"    
    "g_L", "nS", "10nS", "Leak conductance"    
    "E_Na", "mV", "50mV", "Sodium reversal potential"    
    "E_K", "mV", "-100mV", "Potassium reversal potential"    
    "E_L", "mV", "-67mV", "Leak reversal potential (a.k.a. resting potential)"    
    "V_Tr", "mV", "-20mV", "Spike threshold"    
    "refr_T", "ms", "2ms", "Duration of refractory period"    
    "tau_syn_exc", "ms", "0.2ms", "Rise time of the excitatory synaptic alpha function"    
    "tau_syn_inh", "ms", "2ms", "Rise time of the inhibitory synaptic alpha function"    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "V_m_init", "Membrane potential"    
    "V_m_old", "mV", "V_m_init", "Membrane potential at previous timestep for threshold check"    
    "refr_t", "ms", "0ms", "Refractory period timer"    
    "Act_m", "real", "alpha_m_init / (alpha_m_init + beta_m_init)", "Activation variable m for Na"    
    "Inact_h", "real", "alpha_h_init / (alpha_h_init + beta_h_init)", "Inactivation variable h for Na"    
    "Act_n", "real", "alpha_n_init / (alpha_n_init + beta_n_init)", "Activation variable n for K"




Equations
+++++++++



.. math::
   \frac{ dAct_{n} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{n} \cdot (1 - Act_{n}) - \beta_{n} \cdot Act_{n}) } \right) 

.. math::
   \frac{ dAct_{m} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{m} \cdot (1 - Act_{m}) - \beta_{m} \cdot Act_{m}) } \right) 

.. math::
   \frac{ dInact_{h} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{h} \cdot (1 - Inact_{h}) - \beta_{h} \cdot Inact_{h}) } \right) 

.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-(I_{Na} + I_{K} + I_{L}) + I_{e} + I_{stim} + I_{syn,exc} - I_{syn,inh}) } \right) 

.. math::
   \frac{ drefr_{t} } { dt }= \frac{ -1000.0 \cdot \mathrm{ms} } { \mathrm{s} }



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `traub_psc_alpha_neuron <https://github.com/nest/nestml/tree/master/models/neurons/traub_psc_alpha_neuron.nestml>`_.

.. include:: traub_psc_alpha_neuron_characterisation.rst


.. footer::

   Generated at 2026-02-04 14:40:55.047151
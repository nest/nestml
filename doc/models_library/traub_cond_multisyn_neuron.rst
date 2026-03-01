traub_cond_multisyn_neuron
##########################

traub_cond_multisyn - Traub model according to Borgers 2017


Description
+++++++++++

Reduced Traub-Miles Model of a Pyramidal Neuron in Rat Hippocampus [1]_.
parameters got from reference [2]_ chapter 5.

AMPA, NMDA, GABA_A, and GABA_B conductance-based synapses with
beta-function (difference of two exponentials) time course corresponding
to "hill_tononi" model.

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

    
    "C_m", "pF", "100.0pF", "Membrane capacitance"    
    "g_Na", "nS", "10000.0nS", "Sodium peak conductance"    
    "g_K", "nS", "8000.0nS", "Potassium peak conductance"    
    "g_L", "nS", "10nS", "Leak conductance"    
    "E_Na", "mV", "50.0mV", "Sodium reversal potential"    
    "E_K", "mV", "-100.0mV", "Potassium reversal potentia"    
    "E_L", "mV", "-67.0mV", "Leak reversal potential (a.k.a. resting potential)"    
    "V_Tr", "mV", "-20.0mV", "Spike threshold"    
    "refr_T", "ms", "2ms", "Duration of refractory period"    
    "AMPA_g_peak", "nS", "0.1nS", "Parameters for synapse of type AMPA, GABA_A, GABA_B and NMDApeak conductance"    
    "AMPA_E_rev", "mV", "0.0mV", "reversal potential"    
    "tau_AMPA_1", "ms", "0.5ms", "rise time"    
    "tau_AMPA_2", "ms", "2.4ms", "decay time, Tau_1 < Tau_2"    
    "NMDA_g_peak", "nS", "0.075nS", "peak conductance"    
    "tau_NMDA_1", "ms", "4.0ms", "rise time"    
    "tau_NMDA_2", "ms", "40.0ms", "decay time, Tau_1 < Tau_2"    
    "NMDA_E_rev", "mV", "0.0mV", "reversal potential"    
    "NMDA_Vact", "mV", "-58.0mV", "inactive for V << Vact, inflection of sigmoid"    
    "NMDA_Sact", "mV", "2.5mV", "scale of inactivation"    
    "GABA_A_g_peak", "nS", "0.33nS", "peak conductance"    
    "tau_GABAA_1", "ms", "1.0ms", "rise time"    
    "tau_GABAA_2", "ms", "7.0ms", "decay time, Tau_1 < Tau_2"    
    "GABA_A_E_rev", "mV", "-70.0mV", "reversal potential"    
    "GABA_B_g_peak", "nS", "0.0132nS", "peak conductance"    
    "tau_GABAB_1", "ms", "60.0ms", "rise time"    
    "tau_GABAB_2", "ms", "200.0ms", "decay time, Tau_1 < Tau_2"    
    "GABA_B_E_rev", "mV", "-90.0mV", "reversal potential for intrinsic current"    
    "I_e", "pA", "0pA", "constant external input current"



State variables
+++++++++++++++

.. csv-table::
    :header: "Name", "Physical unit", "Default value", "Description"
    :widths: auto

    
    "V_m", "mV", "-70.0mV", "Membrane potential"    
    "V_m_old", "mV", "E_L", "Membrane potential at previous timestep for threshold check"    
    "refr_t", "ms", "0ms", "Refractory period timer"    
    "Act_m", "real", "alpha_m_init / (alpha_m_init + beta_m_init)", "Activation variable m for Na"    
    "Inact_h", "real", "alpha_h_init / (alpha_h_init + beta_h_init)", "Inactivation variable h for Na"    
    "Act_n", "real", "alpha_n_init / (alpha_n_init + beta_n_init)", "Activation variable n for K"    
    "g_AMPA", "real", "0", ""    
    "g_NMDA", "real", "0", ""    
    "g_GABAA", "real", "0", ""    
    "g_GABAB", "real", "0", ""    
    "g_AMPA$", "real", "AMPAInitialValue", ""    
    "g_NMDA$", "real", "NMDAInitialValue", ""    
    "g_GABAA$", "real", "GABA_AInitialValue", ""    
    "g_GABAB$", "real", "GABA_BInitialValue", ""




Equations
+++++++++



.. math::
   \frac{ dV_{m} } { dt }= \frac 1 { C_{m} } \left( { (-(I_{Na} + I_{K} + I_{L}) + I_{e} + I_{stim} + I_{syn}) } \right) 

.. math::
   \frac{ drefr_{t} } { dt }= \frac{ -1000.0 \cdot \mathrm{ms} } { \mathrm{s} }

.. math::
   \frac{ dAct_{n} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{n} \cdot (1 - Act_{n}) - \beta_{n} \cdot Act_{n}) } \right) 

.. math::
   \frac{ dAct_{m} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{m} \cdot (1 - Act_{m}) - \beta_{m} \cdot Act_{m}) } \right) 

.. math::
   \frac{ dInact_{h} } { dt }= \frac 1 { \mathrm{ms} } \left( { (\alpha_{h} \cdot (1 - Inact_{h}) - \beta_{h} \cdot Inact_{h}) } \right) 



Source code
+++++++++++

The model source code can be found in the NESTML models repository here: `traub_cond_multisyn_neuron <https://github.com/nest/nestml/tree/master/models/neurons/traub_cond_multisyn_neuron.nestml>`_.

.. include:: traub_cond_multisyn_neuron_characterisation.rst


.. footer::

   Generated at 2026-02-04 14:40:55.368302
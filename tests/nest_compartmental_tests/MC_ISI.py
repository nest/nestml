#
# MC_ISI
#
# First version: 25/09/2024
# Author: Elena Pastorelli, INFN, Rome (IT)
#
# Description: Comparison between ISI of pure somatic DC input in Ca-AdEx vs AdEx
# The AdEx is built with a specific set of parameters agains which the multi-comp had been fitted
#



import nest
import numpy as np
import matplotlib.pyplot as plt
import random
import statistics as stat
import sys
import yaml



"""
0 - Poisson
1 - single exc spike on ALPHA
2 - single exc spikes of increasing weight on ALPHA
3 - single inh spike on ALPHA
4 - single inh spike on GABA
5 - single spikes of increasing weight on ALPHA
6 - single spikes of increasing weight on GABA
"""

action = 1


stimulusStart = 10000
stimulusDuration = 2000
stimulusStop = stimulusStart + stimulusDuration
SimTime = stimulusStop + 3000
countWindow = stimulusDuration


I_s = 300

aeif_dict = {
    "a": 0.,
    "b": 40.,
    "t_ref": 0.,
    "Delta_T": 2.,
    "C_m": 200.,
    "g_L": 10.,
    "E_L": -63.,
    "V_reset": -65.,
    "tau_w": 500.,
    "V_th": -50.,
    "V_peak": -40.,
    }

cm_dict = {
    "C_mD": 10.0,
    "C_m": 362.5648533496359,
    "Ca_0": 0.0001,
    "Ca_th": 0.00043,
    "V_reset": -62.12885359171539,
    #"d_BAP": 2.4771369535227308,
    "Delta_T": 2.0,
    "E_K": -90.0,
    "E_LD": -80.0,
    "E_L": -58.656837907086036,
    "V_th": -50.0,
    "exp_K_Ca": 4.8,
    "g_C": 17.55192973190035,
    #"g_C": 0.0,
    "g_LD": 2.5088334130360064,
    "g_L": 6.666182946322264,
    "g_Ca": 22.9883727668534,
    "g_K": 18.361017565618574,
    "h_half_Ca": -21.0,
    "h_slope_Ca": -0.5,
    "m_half_Ca": -9.0,
    "m_slope_Ca": 0.5,
    "phi_ca": 2.200252914099994e-08,
    "refr_T": 0.0,
    "tau_Ca": 129.45363748885939,
    "tau_h_Ca": 80.0,
    "tau_m_Ca": 15.0,
    "tau_K": 1.0,
    #"w_BAP": 32.39598141845997,
    "tau_w": 500.0,
    "a": 0,
    "b": 40.0,
    "V_peak": -40.0,
    }

w_BAP = 32.39598141845997
d_BAP = 2.4771369535227308

nest.ResetKernel()

nest.Install('nestmlmodule')

aeif = nest.Create("aeif_cond_alpha", params=aeif_dict)
cm = nest.Create('aeif_cond_alpha_neuron', params=cm_dict)
#nest.Connect(cm, cm, syn_spec={'synapse_model': 'static_synapse', 'weight': w_BAP, 'delay': d_BAP, 'receptor_type': 1})

#############################
# Test for Poisson stimulus #
#############################

if action == 0:

	SimTime = 10
	stimulusStart = 0.0
	stimulusStop = SimTime
	countWindow = stimulusStop-stimulusStart
	
	# Poisson parameters
	spreading_factor = 4
	basic_rate = 600.0
	basic_weight = 0.6
	weight = basic_weight * spreading_factor
	rate = basic_rate / spreading_factor

	cf = 1.
 
	# Create and connct Poisson generator
	pg0 = nest.Create('poisson_generator', 20, params={'rate': rate, 'start': stimulusStart, 'stop': stimulusStop})
	nest.Connect(pg0, cm, syn_spec={'synapse_model': 'static_synapse', 'weight': weight*cf, 'delay': 1., 'receptor_type': 0})
	nest.Connect(pg0, aeif, syn_spec={'synapse_model': 'static_synapse', 'weight': weight, 'delay': 1.})

#############################
# Test for spike generator  #
#############################

elif action == 1:
	
	SimTime = 100
	stimulusStart = 0.0
	stimulusStop = SimTime
	countWindow = stimulusStop-stimulusStart
	
	weight = 300
	cf = 1.

	# Create and connct spike generator
	sg0 = nest.Create('spike_generator', 1, {'spike_times': [50]})
	nest.Connect(sg0, cm, syn_spec={'synapse_model': 'static_synapse', 'weight': weight, 'delay': 1., 'receptor_type': 0})
	nest.Connect(sg0, aeif, syn_spec={'synapse_model': 'static_synapse', 'weight': weight, 'delay': 1.})

#############################
# Test for DC input         #
#############################

elif action == 2:

	# Create and connect current generators (to soma in cm)
	dcgs = nest.Create('dc_generator', {'start': stimulusStart, 'stop': stimulusStop, 'amplitude': I_s})
	nest.Connect(dcgs, cm, syn_spec={'synapse_model': 'static_synapse', 'weight': 1., 'delay': .1, 'receptor_type': 0})
	nest.Connect(dcgs, aeif, syn_spec={'synapse_model': 'static_synapse', 'weight': 1., 'delay': .1})


# create multimeters to record compartment voltages and various state variables
rec_list = ['v_comp0', 'v_comp1', 'w_5','m_Ca_1','h_Ca_1','i_AMPA_9']
mm_cm = nest.Create('multimeter', 1, {'record_from': ['V_m','V_mD','w'], 'interval': .1})
mm_aeif = nest.Create('multimeter', 1, {'record_from': ['V_m','w'], 'interval': .1})
nest.Connect(mm_cm, cm)
nest.Connect(mm_aeif, aeif)

# create and connect a spike recorder
sr_cm = nest.Create('spike_recorder')
sr_aeif = nest.Create('spike_recorder')
nest.Connect(cm, sr_cm)
nest.Connect(aeif, sr_aeif)

nest.Simulate(SimTime)

print('I_s current = ', I_s)

res_cm = nest.GetStatus(mm_cm, 'events')[0]
events_cm = nest.GetStatus(sr_cm)[0]['events']
res_aeif = nest.GetStatus(mm_aeif, 'events')[0]
events_aeif = nest.GetStatus(sr_aeif)[0]['events']

totalSpikes_cm = sum(map(lambda x: x>stimulusStart and x<stimulusStop, events_cm['times']))
totalSpikes_aeif = sum(map(lambda x: x>stimulusStart and x<stimulusStop, events_aeif['times']))
print("Total spikes multiComp = ", totalSpikes_cm)
print("Total spikes adex      = ", totalSpikes_aeif)
print("FR multiComp           = ", totalSpikes_cm*1000/countWindow)
print("FR adex                = ", totalSpikes_aeif*1000/countWindow)

print("Spike times multiComp:\n")
print(events_cm['times'])
print("Spike times adex:\n")
print(events_aeif['times'])

plt.figure('ISI @ Is = '+ str(I_s))
###############################################################################
plt.subplot(411)
plt.plot(res_aeif['times'], res_aeif['V_m'], c='r', label='v_m adex')
plt.plot(res_cm['times'], res_cm['V_m'], c='b', label='v_m soma cm')
plt.plot(res_cm['times'], res_cm['V_mD'], c='g', label='v_m dist cm')
plt.legend()
plt.xlim(0, SimTime)
plt.ylabel('Vm [mV]')
plt.title('MultiComp (blue) and adex (red) voltage')

plt.subplot(412)
#plt.plot(res_cm['times'], res_cm['m_Ca_1'], c='b', ls='--', lw=2., label='m')
#plt.plot(res_cm['times'], res_cm['h_Ca_1'], c='r', ls='--', lw=2., label='h')
#plt.plot(res_cm['times'], res_cm['m_Ca_1']*res_cm['h_Ca_1'], c='k', ls='--', lw=2., label='g')
plt.legend()
plt.xlim(0, SimTime)
plt.ylabel('Ca')
plt.title('Distal Ca activation')

plt.subplot(413)
plt.plot(res_cm['times'], res_cm['w'], c='b', ls='--', lw=2., label='W cm')
plt.plot(res_aeif['times'], res_aeif['w'], c='r', ls='--', lw=2., label='W adex')
plt.legend()
plt.xlim(0, SimTime)
plt.ylabel('W')
plt.title('Adaptation')

plt.subplot(414)
events_cm = nest.GetStatus(sr_cm)[0]['events']
plt.eventplot(events_cm['times'],linelengths = 0.2,color = 'b')
events_aeif = nest.GetStatus(sr_aeif)[0]['events']
plt.eventplot(events_aeif['times'],linelengths = 0.2,color = 'r')
plt.xlim(0, SimTime)
plt.ylabel('Spikes')
plt.title('Raster - cm (blue) VS adex (red)')
plt.xlabel('Time [ms]')

plt.show()

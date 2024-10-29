#
# RELU code with DC stimulation
#
# First version: 25/01/2023
# Author: Elena Pastorelli, INFN, Rome (IT)
#
# Description: code adapted from MC-Adex-BAC optimizee
#


from collections import namedtuple

import numpy as np
import matplotlib.pyplot as plt
import random
import statistics as stat
import sys
import yaml
import time
import datetime

from utility_RELU import stimula, stimulaNoisy, spikeInSteps, stimula_soma, FRInLastSilence
from plot_FR import plot_FR, plot_FR1, plot_FR_paper

class MCADEXBACOptimizee():

    def __init__(self):

        return


    def simulate(self):
        """
        :param ~l2l.utils.trajectory.Trajectory traj: Trajectory
        :return: a single element :obj:`tuple` containing the fitness of the simulation
        """
        global nest
        import nest
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        self.comm = comm
        self.rank = self.comm.Get_rank()
        assert (nest.Rank() == self.rank)
        print(self.rank)
        self.__init__()
        individual = self.create_individual()
        print(individual)
        #self.id = traj.individual.ind_idx
        
        self.C_m_d = individual['C_m_d']
        self.C_m_s = individual['C_m_s']
        self.delta_T = individual['delta_T']
        self.e_K = individual['e_K']
        self.e_L_d = individual['e_L_d']
        self.e_L_s = individual['e_L_s']
        self.e_Na_Adex = individual['e_Na_Adex']
        self.g_C_d = individual['g_C_d']
        self.g_L_d = individual['g_L_d']
        self.g_L_s = individual['g_L_s']
        self.gbar_Ca = individual['gbar_Ca']
        self.gbar_K_Ca = individual['gbar_K_Ca']
        self.phi = individual['phi']
        self.tau_decay_Ca = individual['tau_decay_Ca']
        self.m_half = individual['m_half']
        self.h_half = individual['h_half']
        self.m_slope = individual['m_slope']
        self.h_slope = individual['h_slope']
        self.tau_m = individual['tau_m']
        self.tau_h = individual['tau_h']
        self.tau_m_K_Ca = individual['tau_m_K_Ca']
        self.Ca_th = individual['Ca_th']
        self.exp_K_Ca = individual['exp_K_Ca']
        self.t_ref = individual['t_ref']
        self.d_BAP = individual['d_BAP']
        self.w_BAP = individual['w_BAP']
        self.V_reset = individual['V_reset']
        self.g_w = individual['g_w']

        # simulation step (ms).
        self.dt = 0.1
        self.local_num_threads = 1

        plotVars = 0
        silence = 3000
        stimulusStart = 0.
        stimulusDuration = 2000.
        Is_start = 0.
        Is_end = 1000.   
        Id_start = 0.
        Id_end = 1000.
        delta_mu = 40
        step = int((Id_end-Id_start)//delta_mu)
        sigma = 0

        SimTime = step * (stimulusDuration + silence)
        I = np.arange(Is_start,Is_end,delta_mu)
        extent=[Is_start,Is_end,Id_end,Id_start]
                
        self.neuron_model = 'cm_default'

        self.soma_params = {'C_m': self.C_m_s,                   # [pF] Soma capacitance
                            'g_L': self.g_L_s,                   # [nS] Soma leak conductance
                            'e_L': self.e_L_s,                   # [mV] Soma reversal potential
                            'gbar_Na_Adex': self.g_L_s,          # [nS] Adex conductance
                            'e_Na_Adex': self.e_Na_Adex,         # [mV] Adex threshold
                            'delta_T': self.delta_T              # [mV] Adex slope factor
                            }

        self.distal_params = {'C_m': self.C_m_d,                 # [pF] Distal capacitance
                              'g_L': self.g_L_d,                 # [nS] Distal leak conductance
                              'g_C': self.g_C_d,                 # [nS] Soma-distal coupling conductance
                              'e_L': self.e_L_d,                 # [mV] Distal reversal potential
                              'gbar_Ca': self.gbar_Ca,           # [nS] Ca maximal conductance
                              'gbar_K_Ca': self.gbar_K_Ca,       # [nS] K_Ca maximal conductance
                              'e_K': self.e_K,                   # [mV] K reversal potential
                              'tau_decay_Ca': self.tau_decay_Ca, # [ms] decay of Ca concentration
                              'phi': self.phi,                   # [-] scale factor
                              'm_half': self.m_half,             # [mV] m half-value for Ca
                              'h_half': self.h_half,             # [mV] h half-value for Ca
                              'm_slope': self.m_slope,           # [-] m slope factor for Ca
                              'h_slope': self.h_slope,           # [-] h slope factor for Ca
                              'tau_m': self.tau_m,               # [ms] m tau decay for Ca
                              'tau_h': self.tau_h,               # [ms] h tau decay dor Ca
                              'tau_m_K_Ca': self.tau_m_K_Ca,     # [ms] m tau decay for K_Ca
                              'Ca_0': self.default_param["Ca_0"],# [mM] Baseline intracellular Ca conc
                              'Ca_th': self.Ca_th,               # [mM] Threshold Ca conc for Ca channel opening
                              'exp_K_Ca': self.exp_K_Ca          # [-] Exponential factor in K_Ca current with Hay dyn
                              }
        

        #==============================================================================
        # Soma and dist
        #==============================================================================
        
        spikesInStep_somadist = []
        events_somadist = []

        print("Current Time: ", datetime.datetime.now())

        n_neu = int((Id_end-Id_start)//delta_mu)   ## same value as "step"
        print('Total number of neurons: ', n_neu)

        Tstart = time.time()
        
        nest.ResetKernel()
        nest.set_verbosity('M_ERROR')
        nest.SetKernelStatus({'resolution': self.dt})
        nest.SetKernelStatus({'local_num_threads':self.local_num_threads})

        #self.create_cm_neuron(n_neu)
	self.cm = nest.Create(xxx)
        sr = nest.Create('spike_recorder',n_neu)
        nest.Connect(self.cm, sr, 'one_to_one')

        mu0 = Is_start
        sigma0 = sigma
        delta_mu0 = delta_mu
        step0 = step
        sigma1 = sigma
        delta_mu1 = 0.
        step1 = step
        neuID = 0

        for index in range(int(Id_start),int(Id_end),delta_mu):

            print("Iteration n. ", index//delta_mu)

            mu1 = index
            
            ###############################################################################
            # create and connect current generators to compartments
            stimula(self.cm[neuID],stimulusStart,stimulusDuration,mu0,sigma0,delta_mu0,step0,mu1,sigma1,delta_mu1,step1,silence)
            neuID = neuID + 1
            
        print("Simulation started")
        nest.Simulate(SimTime)

        neuID = 0
        for index in range(int(Id_start),int(Id_end),delta_mu):

            print("Results from iteration n. ", index//delta_mu)

            events_somadist_values = nest.GetStatus(sr[neuID])[0]['events']
            events_somadist.append(events_somadist_values['times'])
            spikesInStep_somadist.append(spikeInSteps(events_somadist_values,stimulusStart,stimulusDuration,step0,silence))
            neuID = neuID + 1
        
        #==============================================================================
        # End simulation
        #==============================================================================
        Tend = time.time()
        print("Simulation completed")
        print('Execution time: ', Tend-Tstart)

        #==============================================================================
        # Plot
        #==============================================================================
        print("Elaborating plot...")
        print("firing_grid size is ", len(spikesInStep_somadist))
        fr=spikesInStep_somadist
        fig=plot_FR_paper(fr, extent, yInvert=1, maskWhite=1, contour=1, centralAxis=1, Dlevels=10)

        Id_current = np.arange(Id_start,Id_end,delta_mu)
        spikesInStep_dist = [spikesInStep_somadist[i][np.argmax(Id_current==0)] for i in range (n_neu)]
        label_somadist = 'soma + dist @' + str(Id_end)

        return(spikesInStep_somadist,events_somadist)       

myRun = MCADEXBACOptimizee()
firing_grid,events_grid = myRun.simulate()

plt.show()

# -*- coding: utf-8 -*-
#
# test_spinnaker_stdp.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

import os
import matplotlib.pyplot as plt
import numpy as np
import pytest

from pynestml.frontend.pynestml_frontend import generate_spinnaker_target


class TestSpiNNakerSTDP:
    """SpiNNaker code generation tests"""

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_code(self):
        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                  "synapse": "stdp_synapse",
                                                  "post_ports": ["post_spikes"]}],
                        "delay_variable":{"stdp_synapse":"d"},
                        "weight_variable":{"stdp_synapse":"w"}}

        files = [
            os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
            os.path.join("models", "synapses", "stdp_synapse.nestml")
        ]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        target_path = "spinnaker-target"
        install_path = "spinnaker-install"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"
        generate_spinnaker_target(input_path,
                                  target_path=target_path,
                                  install_path=install_path,
                                  logging_level=logging_level,
                                  module_name=module_name,
                                  suffix=suffix,
                                  codegen_opts=codegen_opts)

    def run_sim(self, pre_spike_times, post_spike_times, simtime=1100):
        import pyNN.spiNNaker as p
        from pyNN.utility.plotting import Figure, Panel

        from python_models8.neuron.builds.iaf_psc_exp_neuron_nestml import iaf_psc_exp_neuron_nestml as iaf_psc_exp_neuron_nestml
        from python_models8.neuron.implementations.stdp_synapse_nestml_impl import stdp_synapse_nestmlDynamics as stdp_synapse_nestml

#        p.reset()
        p.setup(timestep=1.0)
        exc_input = "exc_spikes"
        inh_input = "inh_spikes"

        #inputs for pre and post synaptic neurons
        pre_input = p.Population(1, p.SpikeSourceArray(spike_times=[0]), label="pre_input")
        post_input = p.Population(1, p.SpikeSourceArray(spike_times=[0]), label="post_input")

        #pre and post synaptic spiking neuron populations
        pre_spiking = p.Population(1, iaf_psc_exp_neuron_nestml(), label="pre_spiking")
        post_spiking = p.Population(1, iaf_psc_exp_neuron_nestml(), label="post_spiking")

        weight_pre = 3000
        weight_post = 3000

        p.Projection(pre_input, pre_spiking, p.OneToOneConnector(), receptor_type=exc_input, synapse_type=p.StaticSynapse(weight=weight_pre))
        p.Projection(post_input, post_spiking, p.OneToOneConnector(), receptor_type=exc_input, synapse_type=p.StaticSynapse(weight=weight_post))

        stdp_model = stdp_synapse_nestml(weight=250)
        stdp_projection = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type=exc_input)
        #stdp_projection_inh = p.Projection(pre_spiking, post_spiking, p.AllToAllConnector(), synapse_type=stdp_model, receptor_type=inh_input)

        #record spikes
        pre_spiking.record(["spikes"])
        post_spiking.record(["spikes"])

        #pre_input.set(spike_times=[100, 110, 120, 1000])
        pre_input.set(spike_times=pre_spike_times)
        post_input.set(spike_times=post_spike_times)

        p.run(simtime)

        pre_neo = pre_spiking.get_data("spikes")
        post_neo = post_spiking.get_data("spikes")

        pre_spike_times = pre_neo.segments[0].spiketrains
        post_spike_times = post_neo.segments[0].spiketrains

        w_curr = stdp_projection.get("weight", format="float")

        p.end()

        return w_curr[0][0], pre_spike_times, post_spike_times



    def get_trace_at(self,t, t_spikes, tau, initial=0., increment=1., before_increment=False, extra_debug=False):
        if extra_debug:
            print("\t-- obtaining trace at t = " + str(t))
        if len(t_spikes) == 0:
            return initial
        tr = initial
        t_sp_prev = 0.
        for t_sp in t_spikes:
            if t_sp > t:
                break
            if extra_debug:
                _tr_prev = tr
            tr *= np.exp(-(t_sp - t_sp_prev) / tau)
            if t_sp == t:  # exact floating point match!
                if before_increment:
                    if extra_debug:
                        print("\t   [%] exact (before_increment = T), prev trace = " + str(_tr_prev) + " at t = " + str(t_sp_prev)
                              + ", decayed by dt = " + str(t - t_sp_prev) + ", tau = " + str(tau) + " to t = " + str(t) + ": returning trace: " + str(tr))
                    return tr
                else:
                    if extra_debug:
                        print("\t   [%] exact (before_increment = F), prev trace = " + str(_tr_prev) + " at t = " + str(t_sp_prev) + ", decayed by dt = " + str(
                            t - t_sp_prev) + ", tau = " + str(tau) + " to t = " + str(t) + ": returning trace: " + str(tr + increment))
                    return tr + increment
            tr += increment
            t_sp_prev = t_sp
        if extra_debug:
            _tr_prev = tr
        tr *= np.exp(-(t - t_sp_prev) / tau)
        if extra_debug:
            print("\t   [&] prev trace = " + str(_tr_prev) + " at t = " + str(t_sp_prev) + ", decayed by dt = "
                  + str(t - t_sp_prev) + ", tau = " + str(tau) + " to t = " + str(t) + ": returning trace: " + str(tr))
        return tr


    def run_reference_simulation(self,times_spikes_pre,
                                 times_spikes_post,
                                 times_spikes_syn_persp):

        """
        #setup sPyNNaker in order retrieve values from stdp synapse
        import pyNN.spiNNaker as p
        p.setup(timestep=1.0)
        #import stdp model in order to retrieve parameters
        from python_models8.neuron.implementations.stdp_synapse_nestml_impl import stdp_synapse_nestmlDynamics as stdp_synapse_nestml
        stdp_model = stdp_synapse_nestml(weight=0) #0x8000)

        params = stdp_model.get_parameter_names()

        for x in params:
            print(x + " = " + str(stdp_model._nestml_model_variables[x]))
        """
        #set synaptic parameters
        delay = 1
        #SpiNNaker: lambda 0.01
        _lambda = 0.01
        tau_pre = 20
        tau_post = 20

        #parameters not needed right now
        #mu_plus = 1
        #mu_minus = 1

        #SpiNNaker w_max = 100.0
        w_max = 500.0
        #SpiNNaker w_min 0.0
        w_min = -500.0
        #SpiNNaker w_init = 0
        w_init = 0

        #initialize trace variables
        tr_pre = 0
        tr_post = 0

        #initialize weight of simulation
        weight = w_init

        #log = {0.: {"weight": weight, "tr_pre": tr_pre, "tr_post": tr_post}}

        log = {times_spikes_pre[0]: {"weight": weight, "tr_pre": tr_pre, "tr_post": tr_post}}

        for spk_time in np.unique(times_spikes_syn_persp):

            if spk_time in times_spikes_post:
                tr_pre = self.get_trace_at(spk_time, times_spikes_pre,
                                      tau_pre, before_increment=False, extra_debug=True)

                tr_post = self.get_trace_at(spk_time, times_spikes_post,
                                       tau_post, before_increment=True, extra_debug=True)




                dw = _lambda * tr_pre

                old_weight = weight
                weight = np.clip(weight + dw, a_min=w_min, a_max=w_max)
                print("[REF] t = " + str(spk_time) + ": facilitating from " + str(old_weight) + " to " + str(weight) + " with pre tr = " + str(tr_pre) + ", post tr = " + str(tr_post))

            if spk_time in times_spikes_pre:
                tr_post = self.get_trace_at(spk_time, times_spikes_post,
                                       tau_post, before_increment=False, extra_debug=True)

                tr_pre = self.get_trace_at(spk_time, times_spikes_pre,
                                      tau_pre, before_increment=True, extra_debug=True)

                dw = _lambda * tr_post

                old_weight = weight
                weight = np.clip(weight - dw, a_min=w_min, a_max=w_max)
                print("[REF] t = " + str(spk_time) + ": depressing from " + str(old_weight) + " to " + str(weight) + " with pre tr = " + str(tr_pre) + ", post tr = " + str(tr_post))


            log[spk_time] = {"weight": weight, "tr_pre": tr_pre, "tr_post": tr_post}

        #timevec = np.sort(list(log.keys()))
        #weight_reference = np.array([log[k]["weight"] for k in timevec])
        #return timevec, weight_reference


        time = times_spikes_post[0] - times_spikes_pre[0]
        return time,weight

    def test_stdp(self):
        spinn_weightvec = []
        spike_time_axis = []

        pre_spike_times = [250, 1000]

        #save spike times for reference simulation
        ref_post_spike_times = []
        ref_pre_spike_times = []

        d_pts = 10

        for t_post in np.linspace(200, 300, d_pts):
        #for t_post in [450.]:
                dw, actual_pre_spike_times, actual_post_spike_times = self.run_sim(pre_spike_times, [t_post])

                #save spike times for reference simulation
                if len(ref_pre_spike_times) < 2:

                    ref_pre_spike_times.append(float(actual_pre_spike_times[0][0]))
                    ref_pre_spike_times.append(float(actual_pre_spike_times[0][1]))


                ref_post_spike_times.append(float(actual_post_spike_times[0][0]))

                spike_time_axis.append(float(actual_post_spike_times[0][0]) - float(actual_pre_spike_times[0][0]))

                if dw > 16000:   # XXX TODO REMOVE THIS IF...THEN..ELSE
                    spinn_weightvec.append(dw - 32768)
                else:
                    spinn_weightvec.append(dw)

                print("actual pre_spikes: " + str(actual_pre_spike_times))
                print("actual post_spikes: " + str(actual_post_spike_times))
                print("weights after simulation: " + str(dw))

        #!!!
        #convert spinnaker values, bit shift

        #factor 2^(16) = 65536
        # 2^(15) = 32768
        # 2^(14) = 16384
        # 2^(13) = 8192
        conv_factor = 16384

        spinn_weightvec = [x/conv_factor for x in spinn_weightvec]



        print("Simulation results")
        print("------------------")
        print("timevec after sim = " + str(spike_time_axis))
        print("weights after sim = " + str(spinn_weightvec))


        #run reference simulation
        ref_weightvec = []
        ref_timevec = []

        for t_post in ref_post_spike_times:

            all_spike_times = ref_pre_spike_times
            all_spike_times.append(t_post)
            ref_time, ref_weight = self.run_reference_simulation(ref_pre_spike_times, [t_post], all_spike_times)

#            fixed_pre_spike = ref_pre_spike_times[0]
#            all_spike_times = [fixed_pre_spike,t_post]
#            ref_time, ref_weight = self.run_reference_simulation([fixed_pre_spike], [t_post], all_spike_times)

#            print("!!!!!!!!!!!!!WEIGHT REFERENCE!!!!!!!!!!!!!!!!!!!" + str(ref_weight))
#            print("!!!!!!!!!!!!!TIME REFERENCE !!!!!!!!!!!!!!!!!!!!" + str(ref_time))
            ref_weightvec.append(ref_weight)
            ref_timevec.append(ref_time)

        print("spinnaker weight vector:")
        print(spinn_weightvec)

        #adjust reference plot
        vec_diff = spinn_weightvec[0] - ref_weightvec[0]

        ref_weightvec = [x + vec_diff for x in ref_weightvec]

        print("reference weight vector")
        print(ref_weightvec)


        #calculate deviation of reference weight vector and spinnaker weight vector

        vec_dev = []
        for i in range(0,len(ref_timevec)):

            tmp_dev = abs(ref_weightvec[i] - spinn_weightvec[i])

            tmp_dev = abs(tmp_dev)

            vec_dev.append(tmp_dev)


        print("weight deviations vector")
        print(vec_dev)

        #TODO add comparison function here


        fig, ax = plt.subplots()
        #plot spinnaker sim
        ax.plot(spike_time_axis, spinn_weightvec, '.')
        #plot reference sim
        ax.plot(ref_timevec, ref_weightvec, '.')

        ax.set_xlabel(r"$t_{post} - t_{pre} [ms]$")
        ax.set_ylabel(r"$w$")
        ax.set_title("STDP-Window for: "+str(d_pts)+" Datapoints")
        ax.grid(True)


        #create plot for deviations

        fig_dev, ax_dev = plt.subplots()
        #plot spinnaker sim
        ax_dev.plot(spike_time_axis, vec_dev, '.')

        ax_dev.set_xlabel(r"$t_{post} - t_{pre} [ms]$")
        ax_dev.set_ylabel("Absolute Deviations")
        ax_dev.set_title("Weight Deviations From Reference To SpiNNaker Sim." +str(d_pts)+" Datapoints")
        ax_dev.grid(True)

        #create table for vector values and deviations

        columns = [r"$t_{pre} - t_{post} [ms]$","Reference Weights","SpiNNaker Weights","Deviation Percentage"]
        rows = list(zip(ref_timevec,ref_weightvec,spinn_weightvec,vec_dev))


        #create seperate plot for table of values
        fig_table, ax_table = plt.subplots(figsize=(8, len(rows) * 0.5 + 1))
        ax_table.axis('off')

        table = ax_table.table(
            cellText=rows,
            colLabels=columns,
            loc='center',
            cellLoc='center'
        )

        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.2)

        fig_table.tight_layout()
        fig_table.savefig("vector_table.png", bbox_inches='tight', pad_inches=0)
        #plt.close(fig_table)





#        ax.subplots_adjust(bottom=0.2)



        fig.savefig("plot.png")
        fig_table.savefig("vector_table.png", bbox_inches='tight')
        fig_dev.savefig("plot_dev.png")



        #save vectors to textfile


        with open("spinnakerVectors.txt", "w", encoding="utf-8") as f:
            f.write(f"Spike Times 1: {ref_timevec}\n")
            f.write(f" \n")
            f.write(f"Reference Weightvector 2: {ref_weightvec}\n")
            f.write(f" \n")
            f.write(f"SpiNNaker Weightvector 3: {spinn_weightvec}\n")



import time
import numpy as np
import scipy.special as sp
import scipy.stats
import random
import nest
import nest.raster_plot
import matplotlib.pyplot as plt
from pynestml.frontend.pynestml_frontend import generate_nest_target


###############################################################################
# Definition of functions used in this example. First, define the `Lambert W`
# function implemented in SLI. The second function computes the maximum of
# the postsynaptic potential for a synaptic input current of unit amplitude
# (1 pA) using the `Lambert W` function. Thus function will later be used to
# calibrate the synaptic weights.


def LambertWm1(x):
    # Using scipy to mimic the gsl_sf_lambert_Wm1 function.
    return sp.lambertw(x, k=-1 if x < 0 else 0).real


def ComputePSPnorm(tauMem, CMem, tauSyn):
    a = (tauMem / tauSyn)
    b = (1.0 / tauSyn - 1.0 / tauMem)

    # time of maximum
    t_max = 1.0 / b * (-LambertWm1(-np.exp(-1.0 / a) / a) - 1.0 / a)

    # maximum of PSP for current of unit amplitude
    return (np.exp(1.0) / (tauSyn * CMem * b) *
            ((np.exp(-t_max / tauMem) - np.exp(-t_max / tauSyn)) / b -
             t_max * np.exp(-t_max / tauSyn)))

nest.ResetKernel()
nest.local_num_threads = 4

###############################################################################
# Assigning the current time to a variable in order to determine the build
# time of the network.

startbuild = time.time()


###############################################################################
# Assigning the simulation parameters to variables.

dt = .1    # the resolution in ms
delay = 1.5    # synaptic delay in ms

###############################################################################
# Definition of the parameters crucial for asynchronous irregular firing of
# the neurons.

g = 4.0  # ratio inhibitory weight/excitatory weight
epsilon = 0.1  # connection probability

###############################################################################
# Definition of the number of neurons in the network and the number of neurons
# recorded from

#order = 2500
NE = 800  # number of excitatory neurons
NI = 200  # number of inhibitory neurons
N_neurons = NE + NI   # number of neurons in total
N_rec = 50      # record from 50 neurons

###############################################################################
# Definition of connectivity parameters

CE = int(epsilon * NE)  # number of excitatory synapses per neuron
CI = int(epsilon * NI)  # number of inhibitory synapses per neuron
C_tot = int(CI + CE)      # total number of synapses per neuron

n_subgroups = 2  # = n_stimuli
subgroup_size = 50

neuron_model_name = "iaf_psc_exp_nestml__with_neuromodulated_stdp_nestml"
synapse_model_name = "neuromodulated_stdp_nestml__with_iaf_psc_exp_nestml"


# generate_nest_target(input_path=["models/neurons/iaf_psc_exp_alt.nestml", "models/synapses/neuromodulated_stdp.nestml"],
#                      target_path="/tmp/nestml-jit",
#                      logging_level="WARNING",
#                      module_name="nestml_jit_module",
#                      suffix="_nestml",
#                      codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
#                                    "neuron_parent_class_include": "structural_plasticity_node.h",
#                                    "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp",
#                                                              "synapse": "neuromodulated_stdp",
#                                                              "post_ports": ["post_spikes"],
#                                                              "vt_ports": ["mod_spikes"]}]})

nest.Install("nestml_jit_module")


###############################################################################
# Initialization of the parameters of the integrate and fire neuron and the
# synapses. The parameters of the neuron are stored in a dictionary. The
# synaptic currents are normalized such that the amplitude of the PSP is J.

tauSyn = 1.  # synaptic time constant in ms
tauMem = 10.0  # time constant of membrane potential in ms
CMem = 300.0  # capacitance of membrane in in pF
# neuron_params_exc = {"C_m": CMem,
#                  "tau_m": tauMem,
#                  "tau_syn_ex": tauSyn,
#                  "tau_syn_in": tauSyn,
#                  "t_ref": 4.0,
#                  "E_L": -65.,
#                  "V_reset": -70.,
#                  "V_m": -65.,
#                  "V_th": -55.4,
#                  "I_e": 5.   # [pA]
# }
# neuron_params_inh = {"C_m": CMem,
#                  "tau_m": tauMem,
#                  "tau_syn_ex": tauSyn,
#                  "tau_syn_in": tauSyn,
#                  "t_ref": 2.0,
#                  "E_L": -65.,
#                  "V_reset": -70.,
#                  "V_m": -65.,
#                  "V_th": -56.4}

neuron_params_exc = {"C_m": CMem,
                 "tau_m": tauMem,
                 "tau_syn_exc": tauSyn,
                 "tau_syn_inh": tauSyn,
                 "t_ref": 4.0,
                 "E_L": -65.,
                 "V_reset": -70.,
                 "V_m": -65.,
                 "V_th": -55.4,
                 "I_e": 0.   # [pA]
}
neuron_params_inh = {"C_m": CMem,
                 "tau_m": tauMem,
                 "tau_syn_exc": tauSyn,
                 "tau_syn_inh": tauSyn,
                 "t_ref": 2.0,
                 "E_L": -65.,
                 "V_reset": -70.,
                 "V_m": -65.,
                 "V_th": -56.4}

#J = 15.        # postsynaptic amplitude in mV
#J_unit = ComputePSPnorm(tauMem, CMem, tauSyn)
#J_ex = J / J_unit  # amplitude of excitatory postsynaptic current
J_ex = 500.  #100 amplitude of excitatory postsynaptic current
J_in = -g * J_ex    # amplitude of inhibitory postsynaptic current

J_poisson = 2500  # 1.5 nA peak EPSC


learning_rate = 1.   # multiplier for weight updates

reinforced_subgroup_idx = 1
stimulus_rate = 5.   # [s^-1]

min_stimulus_presentation_delay = 10.   # [ms]

# # Izhikevich (2007):
# min_dopa_reinforcement_delay = 10. # [ms]
# max_dopa_reinforcement_delay = 1000. # [ms]

min_dopa_reinforcement_delay = 100. # [ms]
max_dopa_reinforcement_delay = 300. # [ms]

total_t_sim = 50000.  # [ms]

###############################################################################
# Definition of threshold rate, which is the external rate needed to fix the
# membrane potential around its threshold, the external firing rate and the
# rate of the poisson generator which is multiplied by the in-degree CE and
# converted to Hz by multiplication by 1000.

p_rate = 10.   # [Hz]

################################################################################
# Configuration of the simulation kernel by the previously defined time
# resolution used in the simulation. Setting ``print_time`` to `True` prints the
# already processed simulation time as well as its percentage of the total
# simulation time.

nest.resolution = dt
nest.print_time = True
nest.overwrite_files = True

print("Building network")

###############################################################################
# Creation of the nodes using ``Create``. We store the returned handles in
# variables for later reference. Here the excitatory and inhibitory, as well
# as the poisson generator and two spike recorders. The spike recorders will
# later be used to record excitatory and inhibitory spikes. Properties of the
# nodes are specified via ``params``, which expects a dictionary.

nodes_ex = nest.Create(neuron_model_name, NE, params=neuron_params_exc)
nodes_in = nest.Create(neuron_model_name, NI, params=neuron_params_inh)
#noise_ex = nest.Create("poisson_generator", NE, params={"rate": p_rate})
#noise_in = nest.Create("poisson_generator", NI, params={"rate": p_rate})
noise = nest.Create("poisson_generator", params={"rate": p_rate})
vt_spike_times = []
vt_sg = nest.Create("spike_generator",
                    params={"spike_times": vt_spike_times,
                            "allow_offgrid_times": True})

espikes = nest.Create("spike_recorder")
ispikes = nest.Create("spike_recorder")
spikedet_vt = nest.Create("spike_recorder")

# create  volume transmitter
vt = nest.Create("volume_transmitter")
vt_parrot = nest.Create("parrot_neuron")
nest.Connect(vt_sg, vt_parrot)
nest.Connect(vt_parrot, vt, syn_spec={"synapse_model": "static_synapse",
                                      "weight": 1.,
                                      "delay": 1.})   # delay is ignored?!
vt_gid = vt.get("global_id")


# set up custom synapse models
wr = nest.Create("weight_recorder")
nest.CopyModel(synapse_model_name, "excitatory",
               {"weight_recorder": wr, "w": J_ex, "the_delay": delay, "receptor_type": 0,
                "vt": vt_gid, "A_plus": learning_rate * 1., "A_minus": learning_rate * 1.5})

nest.CopyModel("static_synapse", "inhibitory",
               {"weight": J_in, "delay": delay})
nest.CopyModel("static_synapse", "poisson",
               {"weight": J_poisson, "delay": delay})

# make subgroups: pick from excitatory population. subgroups can overlap, but each group consists of 50 unique neurons
subgroup_indices = n_subgroups * [[]]
for i in range(n_subgroups):
    ids_nonoverlapping = False
    while not ids_nonoverlapping:
        ids = np.random.randint(0, NE, subgroup_size)
        ids_nonoverlapping = len(np.unique(ids)) == subgroup_size

    ids.sort()
    subgroup_indices[i] = ids
    
# make one spike generator and one parrot neuron for each subgroup
stim_sg = nest.Create("spike_generator", n_subgroups)
stim_parrots = nest.Create("parrot_neuron", n_subgroups)
stim_spikes_rec = nest.Create("spike_recorder")

nest.Connect(stim_parrots, stim_spikes_rec, syn_spec="static_synapse")

    
print("Connecting network")

nest.Connect(noise, nodes_ex + nodes_in, syn_spec="poisson")

mm = nest.Create("multimeter", params={'record_from': ['V_m'], 'interval': dt})
mms = [nest.Create("multimeter", params={'record_from': ['V_m'], 'interval': dt}) for _ in range(10)]
nest.Connect(mm, nodes_ex[0])
[nest.Connect(mms[i], nodes_ex[i]) for i in range(10)]

nest.Connect(stim_sg, stim_parrots, "one_to_one")

for i in range(n_subgroups):
        nest.Connect(stim_parrots[i], nodes_ex[subgroup_indices[i]], "all_to_all", syn_spec={"weight": 5000.})

conn_params_ex = {'rule': 'fixed_indegree', 'indegree': CE}
nest.Connect(nodes_ex, nodes_ex + nodes_in, conn_params_ex, "excitatory")

conn_params_in = {'rule': 'fixed_indegree', 'indegree': CI}
nest.Connect(nodes_in, nodes_ex + nodes_in, conn_params_in, "inhibitory")

nest.Connect(vt_parrot, spikedet_vt)

nest.Connect(nodes_ex, espikes, syn_spec="static_synapse")
nest.Connect(nodes_in, ispikes, syn_spec="static_synapse")



syn = nest.GetConnections(source=nodes_ex, synapse_model="excitatory")

###############################################################################
# Storage of the time point after the buildup of the network in a variable.

endbuild = time.time()


# generate stimulus timings (input stimulus and reinforcement signal)
t_dopa_spikes = []
t_pre_sg_spikes = [[] for _ in range(n_subgroups)]   # mapping from subgroup_idx to a list of spike (or presentation) times of that subgroup

t = 0.   # [ms]
ev_timestamps = []
while t < total_t_sim:
    # jump to time of next stimulus presentation
    dt_next_stimulus = max(min_stimulus_presentation_delay, np.round(random.expovariate(stimulus_rate) * 1000)) # [ms]
    t += dt_next_stimulus

    ev_timestamps.append(t)
    
    # apply stimulus
    subgroup_idx = np.random.randint(0, n_subgroups)
    t_pre_sg_spikes[subgroup_idx].append(t)

    # reinforce?
    if subgroup_idx == reinforced_subgroup_idx:
        # fire a dopa spike some time after the current time
        t_dopa_spike = t + min_dopa_reinforcement_delay + np.random.randint(max_dopa_reinforcement_delay - min_dopa_reinforcement_delay)
        t_dopa_spikes.append(t_dopa_spike)

print("Stimuli will be presented at times: " + str(ev_timestamps))
        
# set the spike times in the spike generators
for i in range(n_subgroups):
    t_pre_sg_spikes[i].sort()
    stim_sg[i].spike_times = t_pre_sg_spikes[i]

t_dopa_spikes.sort()
vt_sg.spike_times = t_dopa_spikes

for i in range(n_subgroups):
    print("t_pre_sg_spikes[" + str(i) + "] = " + str(t_pre_sg_spikes[i]))
print("t_dopa_spikes = " + str(t_dopa_spikes))

# run the simulation
print("Simulating")

nest.Simulate(total_t_sim)
    
endsimulate = time.time()

###############################################################################
# Reading out the total number of spikes received from the spike recorder
# connected to the excitatory population and the inhibitory population.

print("Actual times of stimulus presentation: " + str(stim_spikes_rec.events["times"]))
print("Actual t_dopa_spikes = " + str(spikedet_vt.get("events")))

events_ex = espikes.n_events
events_in = ispikes.n_events

###############################################################################
# Calculation of the average firing rate of the excitatory and the inhibitory
# neurons by dividing the total number of recorded spikes by the number of
# neurons recorded from and the simulation time. The multiplication by 1000.0
# converts the unit 1/ms to 1/s=Hz.

rate_ex = events_ex / total_t_sim * 1000.0 / N_rec
rate_in = events_in / total_t_sim * 1000.0 / N_rec

###############################################################################
# Reading out the number of connections established using the excitatory and
# inhibitory synapse model. The numbers are summed up resulting in the total
# number of synapses.

num_synapses = (nest.GetDefaults("excitatory")["num_connections"] +
                nest.GetDefaults("inhibitory")["num_connections"])

###############################################################################
# Establishing the time it took to build and simulate the network by taking
# the difference of the pre-defined time variables.

build_time = endbuild - startbuild
sim_time = endsimulate - endbuild

###############################################################################
# Printing the network properties, firing rates and building times.

print("Brunel network simulation (Python)")
print(f"Number of neurons : {N_neurons}")
print(f"Number of synapses: {num_synapses}")
print(f"       Exitatory  : {int(CE * N_neurons) + N_neurons}")
print(f"       Inhibitory : {int(CI * N_neurons)}")
print(f"Excitatory rate   : {rate_ex:.2f} Hz")
print(f"Inhibitory rate   : {rate_in:.2f} Hz")
print(f"Building time     : {build_time:.2f} s")
print(f"Simulation time   : {sim_time:.2f} s")

###############################################################################
# Plot a raster of the excitatory neurons and a histogram.

group_weight_times = [[] for _ in range(n_subgroups)]
group_weight_values = [[] for _ in range(n_subgroups)]
                                        
senders = np.array(wr.events["senders"])
                               
for subgroup_idx in range(n_subgroups):
    nodes_ex_gids = nodes_ex[subgroup_indices[subgroup_idx]].tolist()
    idx = [np.where(senders == nodes_ex_gids[i])[0] for i in range(subgroup_size)]
    idx = [item for sublist in idx for item in sublist]
    group_weight_times[subgroup_idx] = wr.events["times"][idx]
    group_weight_values[subgroup_idx] = wr.events["weights"][idx]

fig, ax = plt.subplots()
for subgroup_idx in range(n_subgroups):
    if subgroup_idx == reinforced_subgroup_idx:
        c = "red"
        zorder=99
    else:
        c = "blue"
        zorder=1
        
    ax.scatter(group_weight_times[subgroup_idx], group_weight_values[subgroup_idx], c=c, alpha=.5, zorder=zorder)

    
plt.show()
    
# timevec = [[] for _ in range(n_subgroups)]   # for each subgroup, the list of times when its weights were recorded
# weight_records_per_subgroup = [[] for _ in range(n_subgroups)]

# senders = np.array(wr.events["senders"])
# N_datapoints = len(wr.events["senders"])
# for subgroup_idx in range(n_subgroups):
#     nodes_ex_gids = nodes_ex[subgroup_indices[subgroup_idx]].tolist()
#     for i in range(N_datapoints):
#         print("x")
#         if senders[i] in nodes_ex_gids:
#             print("y")
            
#             timevec[subgroup_idx].append(wr.events["times"][i])
#             weight_records_per_subgroup[subgroup_idx].append(wr.events["weights"][i])
#             print("z")
#             continue


fig, ax = plt.subplots()
#ax.plot(mm.get("events")["times"],  mm.get("events")["V_m"], label="V_m")
for i in range(10):
	ax.plot(mms[i].get("events")["times"],  mms[i].get("events")["V_m"], label="V_m")
plt.grid(True)

plt.show()


def _histogram(a, bins=10, bin_range=None, normed=False):
    """Calculate histogram for data.

    Parameters
    ----------
    a : list
        Data to calculate histogram for
    bins : int, optional
        Number of bins
    bin_range : TYPE, optional
        Range of bins
    normed : bool, optional
        Whether distribution should be normalized

    Raises
    ------
    ValueError
    """
    from numpy import asarray, iterable, linspace, sort, concatenate

    a = asarray(a).ravel()

    if bin_range is not None:
        mn, mx = bin_range
        if mn > mx:
            raise ValueError("max must be larger than min in range parameter")

    if not iterable(bins):
        if bin_range is None:
            bin_range = (a.min(), a.max())
        mn, mx = [mi + 0.0 for mi in bin_range]
        if mn == mx:
            mn -= 0.5
            mx += 0.5
        bins = linspace(mn, mx, bins, endpoint=False)
    else:
        if (bins[1:] - bins[:-1] < 0).any():
            raise ValueError("bins must increase monotonically")

    # best block size probably depends on processor cache size
    block = 65536
    n = sort(a[:block]).searchsorted(bins)
    for i in range(block, a.size, block):
        n += sort(a[i:i + block]).searchsorted(bins)
    n = concatenate([n, [len(a)]])
    n = n[1:] - n[:-1]

    if normed:
        db = bins[1] - bins[0]
        return 1.0 / (a.size * db) * n, bins
    else:
        return n, bins

def _make_plot(ts, ts1, node_ids, neurons, hist=True, hist_binwidth=5.0,
               grayscale=False, title=None, xlabel=None):
    """Generic plotting routine.

    Constructs a raster plot along with an optional histogram (common part in
    all routines above).

    Parameters
    ----------
    ts : list
        All timestamps
    ts1 : list
        Timestamps corresponding to node_ids
    node_ids : list
        Global ids corresponding to ts1
    neurons : list
        Node IDs of neurons to plot
    hist : bool, optional
        Display histogram
    hist_binwidth : float, optional
        Width of histogram bins
    grayscale : bool, optional
        Plot in grayscale
    title : str, optional
        Plot title
    xlabel : str, optional
        Label for x-axis
    """
    import matplotlib.pyplot as plt

    plt.figure()

    if grayscale:
        color_marker = ".k"
        color_bar = "gray"
    else:
        color_marker = "."
        color_bar = "blue"

    color_edge = "black"

    if xlabel is None:
        xlabel = "Time (ms)"

    ylabel = "Neuron ID"

    if hist:
        ax1 = plt.axes([0.1, 0.3, 0.85, 0.6])
        plotid = plt.plot(ts1, node_ids, color_marker)
        plt.ylabel(ylabel)
        plt.xticks([])
        xlim = plt.xlim()

        plt.axes([0.1, 0.1, 0.85, 0.17])
        t_bins = np.arange(
            np.amin(ts), np.amax(ts),
            float(hist_binwidth)
        )
        n, _ = _histogram(ts, bins=t_bins)
        num_neurons = len(np.unique(neurons))
        heights = 1000 * n / (hist_binwidth * num_neurons)

        plt.bar(t_bins, heights, width=hist_binwidth, color=color_bar,
                edgecolor=color_edge)
        plt.yticks([
            int(x) for x in
            np.linspace(0.0, int(max(heights) * 1.1) + 5, 4)
        ])
        plt.ylabel("Rate (Hz)")
        plt.xlabel(xlabel)
        plt.xlim(xlim)
        plt.axes(ax1)
    else:
        plotid = plt.plot(ts1, node_ids, color_marker)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    if title is None:
        plt.title("Raster plot")
    else:
        plt.title(title)

    plt.draw()

    return plotid

ev = espikes.get("events")
ts, node_ids = ev["times"], ev["senders"]

_make_plot(ts, ts, node_ids, node_ids, xlabel="Time (ms)")

plt.show()

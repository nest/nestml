# -*- coding: utf-8 -*-
#
# test_axonal_delays.py
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

from typing import List, Optional, Tuple

import numpy as np
import os
import pytest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target


nest_version = NESTTools.detect_nest_version()

MODULE_NAME = "nestml_axonal_delays_module"

NEURON_MODEL = "axonal_delay_test_neuron_nestml"
PAIRED_NEURON_MODEL = "axonal_delay_test_neuron_nestml__with_axonal_delay_test_stdp_pl_synapse_nestml"
PAIRED_SYNAPSE_MODEL = "axonal_delay_test_stdp_pl_synapse_nestml__with_axonal_delay_test_neuron_nestml"
STATIC_SYNAPSE_MODEL = "static_synapse_nestml"
AXONAL_STATIC_SYNAPSE_MODEL = "axonal_delay_test_static_synapse_nestml"

# receptor types of the test neuron
DRIVE_RECEPTOR = 1          # spikes received on this port are repeated
PLASTIC_RECEPTOR = 2        # generic (list-based) spike input buffer
PLASTIC_LTI_RECEPTOR = 3    # linear time-invariant (summed) spike input buffer
RECORDABLE_FOR_RECEPTOR = {PLASTIC_RECEPTOR: "w_received",
                           PLASTIC_LTI_RECEPTOR: "w_received_lti"}

RESOLUTION = .1    # [ms]

STDP_PARAMS = {"lambda": .1,
               "alpha": 1.,
               "mu": .4,
               "tau_plus": 20.,
               "tau_minus": 30.}
W_INIT = 1.

# combinations of (dendritic, axonal) delay [ms]
DELAYS = [(1., 0.),     # purely dendritic delay
          (3., 1.),     # predominantly dendritic delay: no corrections are needed
          (2., 2.),     # equal delays: postsynaptic spikes that reach the synapse together with a presynaptic spike are already known when the presynaptic spike is delivered
          (1., 5.),     # predominantly axonal delay
          (.5, 7.3)]    # predominantly axonal delay, with a critical interval that is longer than the interspike intervals

# Hand-crafted spike times [ms] that exercise critical cases for the delays above, in particular for (1., 5.):
#  - post spike that occurs after a pre spike was emitted, but reaches the synapse before the pre spike (10/12)
#  - two pre spikes within the critical interval of the same post spike (20, 21/23)
#  - pre and post spike that reach the synapse at the same time (40/44)
#  - post spike that reaches the synapse after the pre spike (60/66)
#  - post spike before pre spike (80/82)
#  - two post spikes within the critical interval of the same pre spike (100/101, 102.5)
#  - two pre spikes and two post spikes within each other's critical intervals (120, 121.5/122, 124)
HANDCRAFTED_PRE_SPIKE_TIMES = [10., 20., 21., 40., 60., 82., 100., 120., 121.5]
HANDCRAFTED_POST_SPIKE_TIMES = [12., 23., 44., 66., 80., 101., 102.5, 122., 124.]


def random_spike_times(seed: int, n_spikes: int = 40, t_min: float = 5., t_max: float = 400.) -> List[float]:
    r"""Random spike times on the simulation grid (without duplicates)"""
    rng = np.random.default_rng(seed)
    return sorted(set(np.round(rng.uniform(t_min, t_max, n_spikes) / RESOLUTION) * RESOLUTION))


def random_spike_times_with_min_isi(seed: int, min_isi: float, n_spikes: int = 25, t_min: float = 5., mean_isi: float = 10.) -> List[float]:
    r"""Random spike times on the simulation grid, with a minimum interspike interval"""
    rng = np.random.default_rng(seed)
    return list(np.round((t_min + np.cumsum(min_isi + rng.exponential(mean_isi, n_spikes))) / RESOLUTION) * RESOLUTION)


SPIKE_PATTERNS = {"handcrafted": (HANDCRAFTED_PRE_SPIKE_TIMES, HANDCRAFTED_POST_SPIKE_TIMES),
                  "random": (random_spike_times(seed=1), random_spike_times(seed=2))}

# Spike patterns in which the critical interval of a postsynaptic spike (that is, axonal delay - dendritic delay) never contains more than one presynaptic spike. For more than one presynaptic spike, the NEST built-in synapse ``stdp_pl_synapse_hom_ax_delay`` corrects the synaptic weight correctly, but the corrections of the weights that were already transmitted to the postsynaptic neuron are not attributed to the correct spikes. The corresponding NESTML synapse keeps track of the transmitted weight of each spike.
SPIKE_PATTERNS_SINGLE_PRE_SPIKE_PER_CRITICAL_INTERVAL = {"handcrafted": ([t for t in HANDCRAFTED_PRE_SPIKE_TIMES if t not in [21., 121.5]], HANDCRAFTED_POST_SPIKE_TIMES),
                                                         "random": (random_spike_times_with_min_isi(seed=1, min_isi=8.), random_spike_times(seed=2))}


def stdp_pl_reference(pre_spike_times, post_spike_times, dendritic_delay: float, axonal_delay: float, w_init: float = W_INIT, lambda_: float = STDP_PARAMS["lambda"], alpha: float = STDP_PARAMS["alpha"],
                      mu: float = STDP_PARAMS["mu"], tau_plus: float = STDP_PARAMS["tau_plus"], tau_minus: float = STDP_PARAMS["tau_minus"]) -> Tuple[List[float], float]:
    r"""
    Reference implementation of power-law STDP (as in the NEST models ``stdp_pl_synapse_hom`` and ``stdp_pl_synapse_hom_ax_delay``) with dendritic and axonal delays.

    A presynaptic spike emitted at time t_pre reaches the synapse at t_pre + axonal_delay; a postsynaptic spike emitted at time t_post reaches the synapse at t_post + dendritic_delay. All weight updates are computed in the order of arrival at the synapse, regardless of the order in which the spikes were emitted. If a presynaptic and a postsynaptic spike reach the synapse at the same time, the postsynaptic spike causes facilitation, but does not contribute to the depression caused by the presynaptic spike.

    Returns the weights transmitted for each presynaptic spike and the final weight (after the last presynaptic spike).
    """
    # arrival times at the synapse, in integer time steps (to compare times exactly)
    pre_arrivals = np.round((np.array(sorted(pre_spike_times)) + axonal_delay) / RESOLUTION).astype(int)
    post_arrivals = np.round((np.array(sorted(post_spike_times)) + dendritic_delay) / RESOLUTION).astype(int)

    # merge into a single sequence of events; at equal times, postsynaptic spikes are processed first
    events = [(t, 0) for t in post_arrivals] + [(t, 1) for t in pre_arrivals]
    events.sort()

    w = w_init
    transmitted_weights = []
    for t, is_pre in events:
        if is_pre:
            # depression
            K_minus = np.sum(np.exp(-(t - post_arrivals[post_arrivals < t]) * RESOLUTION / tau_minus))
            w = max(0., w - lambda_ * alpha * w * K_minus)
            transmitted_weights.append(w)
        else:
            if t > pre_arrivals[-1]:
                # the synapse only processes postsynaptic spikes when the next presynaptic spike reaches it
                break

            # facilitation
            K_plus = np.sum(np.exp(-(t - pre_arrivals[pre_arrivals < t]) * RESOLUTION / tau_plus))
            w += lambda_ * w**mu * K_plus

    return transmitted_weights, w


@pytest.mark.skipif(not NESTTools.nest_version_has_axonal_delays(nest_version),
                    reason="This test requires a NEST Simulator version that supports axonal delays")
class TestAxonalDelays:
    r"""
    Test axonal and dendritic delays in generated NEST models (see https://github.com/nest/nest-simulator/pull/2989).

    - Spike-timing dependent plasticity with a NESTML synapse that is co-generated with a NESTML neuron, for different combinations of dendritic and axonal delays. If the axonal delay is at least as large as the dendritic delay, postsynaptic spikes can reach the synapse before presynaptic spikes that were already delivered; the synaptic weight and the weight of the spike that was already sent to the postsynaptic neuron then have to be corrected retrospectively. The resulting weights are compared to a reference implementation and to the NEST built-in synapse ``stdp_pl_synapse_hom_ax_delay``.
    - A NEST built-in STDP synapse with axonal delays targeting a (non co-generated) NESTML neuron, which has to apply weight corrections to its input buffers.
    - Spike delivery times and the user interface for synapses with a total delay and with separate axonal and dendritic delays.
    """

    @pytest.fixture(scope="module", autouse=True)
    def generate_code(self, tmp_path_factory):
        r"""Generate code for the neuron and synapse models, and build the NEST extension module"""
        repo_path = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

        # a copy of the static synapse that is generated with axonal delays
        with open(os.path.join(repo_path, "models", "synapses", "static_synapse.nestml"), "r") as f:
            axonal_static_synapse_model = f.read().replace("model static_synapse:", "model axonal_delay_test_static_synapse:")

        model_path = tmp_path_factory.mktemp("axonal_delay_models")
        axonal_static_synapse_fn = os.path.join(model_path, "axonal_delay_test_static_synapse.nestml")
        with open(axonal_static_synapse_fn, "w") as f:
            f.write(axonal_static_synapse_model)

        input_path = [os.path.join(repo_path, "tests", "nest_tests", "resources", "axonal_delay_test_neuron.nestml"),
                      os.path.join(repo_path, "tests", "nest_tests", "resources", "axonal_delay_test_stdp_pl_synapse.nestml"),
                      os.path.join(repo_path, "models", "synapses", "static_synapse.nestml"),
                      axonal_static_synapse_fn]

        generate_nest_target(input_path=input_path,
                             target_path=str(tmp_path_factory.mktemp("axonal_delay_target")),
                             logging_level="WARNING",
                             module_name=MODULE_NAME,
                             suffix="_nestml",
                             codegen_opts={"neuron_synapse_pairs": [{"neuron": "axonal_delay_test_neuron",
                                                                     "synapses": {"axonal_delay_test_stdp_pl_synapse": {"post_ports": ["post_spikes"]}}}],
                                           "weight_variable": {"axonal_delay_test_stdp_pl_synapse": "w",
                                                               "static_synapse": "w",
                                                               "axonal_delay_test_static_synapse": "w"},
                                           "axonal_delay_synapses": ["axonal_delay_test_stdp_pl_synapse",
                                                                     "axonal_delay_test_static_synapse"],
                                           "linear_time_invariant_spiking_input_ports": ["plastic_spikes_lti"]})

    def _reset_kernel(self):
        nest.ResetKernel()
        NESTTools.set_nest_verbosity("ERROR")
        nest.resolution = RESOLUTION
        try:
            nest.Install(MODULE_NAME)
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass

    def _create_pre_neuron(self, spike_times):
        r"""Create a parrot neuron that emits spikes at the given times"""
        sg = nest.Create("spike_generator", params={"spike_times": np.array(spike_times) - 1.})
        pre_neuron = nest.Create("parrot_neuron")
        nest.Connect(sg, pre_neuron, syn_spec={"delay": 1.})

        return pre_neuron

    def _create_post_neuron(self, model: str, spike_times, params: Optional[dict] = None):
        r"""Create a neuron that emits spikes at the given times (driven by a spike generator)"""
        sg = nest.Create("spike_generator", params={"spike_times": np.array(spike_times) - 1.})
        post_neuron = nest.Create(model, params=params)
        nest.Connect(sg, post_neuron, syn_spec={"delay": 1.,
                                                "receptor_type": 0 if model == "parrot_neuron" else DRIVE_RECEPTOR})

        return post_neuron

    def _get_received_weights(self, mm, recordable: str, arrival_times):
        r"""Return the weights received by the neuron at the given times, as recorded by the multimeter"""
        events = mm.get("events")
        idx = [np.argmin(np.abs(events["times"] - t)) for t in arrival_times]
        np.testing.assert_allclose(events["times"][idx], arrival_times)

        return events[recordable][idx]

    def _simulate(self, synapse_model: str, post_neuron_model: str, dendritic_delay: float, axonal_delay: float, pre_spike_times, post_spike_times, receptor_type: int):
        r"""Simulate a single plastic connection between two neurons that spike at the given times, and return the actual spike times, the weights received by the postsynaptic neuron (if it records them) and the final weight of the synapse"""
        self._reset_kernel()

        if synapse_model == "stdp_pl_synapse_hom_ax_delay":
            nest.SetDefaults(synapse_model, {k: v for k, v in STDP_PARAMS.items() if k != "tau_minus"})
            syn_spec = {"synapse_model": synapse_model,
                        "weight": W_INIT}
            post_neuron_params = {"tau_minus": STDP_PARAMS["tau_minus"]}
        else:
            syn_spec = {"synapse_model": synapse_model,
                        "weight": W_INIT,
                        **STDP_PARAMS}
            post_neuron_params = None

        syn_spec.update({"dendritic_delay": dendritic_delay,
                         "axonal_delay": axonal_delay,
                         "receptor_type": receptor_type})

        pre_neuron = self._create_pre_neuron(pre_spike_times)
        post_neuron = self._create_post_neuron(post_neuron_model, post_spike_times, params=post_neuron_params)
        nest.Connect(pre_neuron, post_neuron, syn_spec=syn_spec)

        sr_pre = nest.Create("spike_recorder")
        sr_post = nest.Create("spike_recorder")
        nest.Connect(pre_neuron, sr_pre)
        nest.Connect(post_neuron, sr_post)

        mm = None
        if post_neuron_model != "parrot_neuron":
            mm = nest.Create("multimeter", params={"record_from": list(RECORDABLE_FOR_RECEPTOR.values()),
                                                   "interval": RESOLUTION})
            nest.Connect(mm, post_neuron)

        nest.Simulate(max(pre_spike_times + post_spike_times) + dendritic_delay + axonal_delay + 10.)

        actual_pre_spike_times = list(sr_pre.get("events")["times"])
        actual_post_spike_times = list(sr_post.get("events")["times"])
        np.testing.assert_allclose(actual_pre_spike_times, pre_spike_times)
        np.testing.assert_allclose(actual_post_spike_times, post_spike_times)

        received_weights = None
        if mm is not None:
            arrival_times = np.array(actual_pre_spike_times) + dendritic_delay + axonal_delay
            received_weights = self._get_received_weights(mm, RECORDABLE_FOR_RECEPTOR[receptor_type], arrival_times)

        final_weight = nest.GetConnections(source=pre_neuron, target=post_neuron).get("weight")

        return received_weights, final_weight, nest.num_corrections

    @pytest.mark.parametrize("pattern", SPIKE_PATTERNS.keys())
    @pytest.mark.parametrize("dendritic_delay,axonal_delay", DELAYS)
    @pytest.mark.parametrize("receptor_type", [PLASTIC_RECEPTOR, PLASTIC_LTI_RECEPTOR])
    def test_nestml_stdp_synapse(self, dendritic_delay: float, axonal_delay: float, pattern: str, receptor_type: int):
        r"""Plasticity in a NESTML synapse (co-generated with a NESTML neuron) with dendritic and axonal delays, including retrospective corrections of the weights of the synapse and the weights received by the postsynaptic neuron"""
        pre_spike_times, post_spike_times = SPIKE_PATTERNS[pattern]

        ref_received_weights, ref_final_weight = stdp_pl_reference(pre_spike_times, post_spike_times, dendritic_delay, axonal_delay)

        received_weights, final_weight, num_corrections = self._simulate(PAIRED_SYNAPSE_MODEL, PAIRED_NEURON_MODEL, dendritic_delay, axonal_delay, pre_spike_times, post_spike_times, receptor_type)

        if axonal_delay <= dendritic_delay:
            # if the axonal delay is equal to the dendritic delay, a postsynaptic spike can only require a correction if it occurs at the same time as the presynaptic spike; as spikes are delivered after the end of the timeslice in which they were emitted, this postsynaptic spike is always already known
            assert num_corrections == 0
        elif pattern == "handcrafted":
            # the hand-crafted spike pattern always requires corrections if the axonal delay is larger than the dendritic delay
            assert num_corrections > 0

        np.testing.assert_allclose(received_weights, ref_received_weights, rtol=1E-9)
        np.testing.assert_allclose(final_weight, ref_final_weight, rtol=1E-9)

        # compare to the NEST built-in synapse with axonal delays
        _, nest_final_weight, nest_num_corrections = self._simulate("stdp_pl_synapse_hom_ax_delay", "parrot_neuron", dendritic_delay, axonal_delay, pre_spike_times, post_spike_times, receptor_type=1)
        np.testing.assert_allclose(final_weight, nest_final_weight, rtol=1E-9)
        assert num_corrections == nest_num_corrections

    @pytest.mark.parametrize("num_threads", [1, 2])
    def test_nestml_stdp_synapses_with_different_delays(self, num_threads: int):
        r"""Several NESTML synapses with different combinations of dendritic and axonal delays that converge onto the same postsynaptic neuron. A single postsynaptic spike can require corrections of several synapses, and the postsynaptic spike history has to be kept for long enough for all of them."""
        self._reset_kernel()
        nest.local_num_threads = num_threads

        post_spike_times = random_spike_times(seed=10, n_spikes=60)
        pre_spike_times = [random_spike_times(seed=11 + i) for i in range(len(DELAYS))]

        post_neuron = self._create_post_neuron(PAIRED_NEURON_MODEL, post_spike_times)
        pre_neurons = []
        for (dendritic_delay, axonal_delay), spike_times in zip(DELAYS, pre_spike_times):
            pre_neuron = self._create_pre_neuron(spike_times)
            nest.Connect(pre_neuron, post_neuron, syn_spec={"synapse_model": PAIRED_SYNAPSE_MODEL,
                                                            "weight": W_INIT,
                                                            "dendritic_delay": dendritic_delay,
                                                            "axonal_delay": axonal_delay,
                                                            "receptor_type": PLASTIC_RECEPTOR,
                                                            **STDP_PARAMS})
            pre_neurons.append(pre_neuron)

        mm = nest.Create("multimeter", params={"record_from": ["w_received"], "interval": RESOLUTION})
        nest.Connect(mm, post_neuron)

        nest.Simulate(max(post_spike_times + sum(pre_spike_times, [])) + 20.)

        assert nest.num_corrections > 0

        # the weights received by the postsynaptic neuron in each timestep are the sum over the synapses
        expected_received_weights = {}
        for (dendritic_delay, axonal_delay), spike_times, pre_neuron in zip(DELAYS, pre_spike_times, pre_neurons):
            ref_received_weights, ref_final_weight = stdp_pl_reference(spike_times, post_spike_times, dendritic_delay, axonal_delay)
            np.testing.assert_allclose(nest.GetConnections(source=pre_neuron, target=post_neuron).get("weight"), ref_final_weight, rtol=1E-9)

            for t, w in zip(spike_times, ref_received_weights):
                t_arrival = np.round((t + dendritic_delay + axonal_delay) / RESOLUTION) * RESOLUTION
                expected_received_weights[t_arrival] = expected_received_weights.get(t_arrival, 0.) + w

        arrival_times = sorted(expected_received_weights.keys())
        received_weights = self._get_received_weights(mm, "w_received", arrival_times)
        np.testing.assert_allclose(received_weights, [expected_received_weights[t] for t in arrival_times], rtol=1E-9)

    @pytest.mark.parametrize("pattern", SPIKE_PATTERNS_SINGLE_PRE_SPIKE_PER_CRITICAL_INTERVAL.keys())
    @pytest.mark.parametrize("dendritic_delay,axonal_delay", DELAYS)
    @pytest.mark.parametrize("receptor_type", [PLASTIC_RECEPTOR, PLASTIC_LTI_RECEPTOR])
    def test_nest_stdp_synapse_to_nestml_neuron(self, dendritic_delay: float, axonal_delay: float, pattern: str, receptor_type: int):
        r"""A NEST built-in STDP synapse with axonal delays that targets a (not co-generated) NESTML neuron: the neuron has to trigger the corrections, and apply the weight corrections to the spikes in its input buffers"""
        pre_spike_times, post_spike_times = SPIKE_PATTERNS_SINGLE_PRE_SPIKE_PER_CRITICAL_INTERVAL[pattern]

        ref_received_weights, ref_final_weight = stdp_pl_reference(pre_spike_times, post_spike_times, dendritic_delay, axonal_delay)

        received_weights, final_weight, num_corrections = self._simulate("stdp_pl_synapse_hom_ax_delay", NEURON_MODEL, dendritic_delay, axonal_delay, pre_spike_times, post_spike_times, receptor_type)

        if axonal_delay > dendritic_delay and pattern == "handcrafted":
            assert num_corrections > 0

        np.testing.assert_allclose(received_weights, ref_received_weights, rtol=1E-9)
        np.testing.assert_allclose(final_weight, ref_final_weight, rtol=1E-9)

    @pytest.mark.parametrize("synapse_model,delays", [(STATIC_SYNAPSE_MODEL, {"delay": 2.5}),
                                                      (AXONAL_STATIC_SYNAPSE_MODEL, {"dendritic_delay": 1.5, "axonal_delay": 2.}),
                                                      (AXONAL_STATIC_SYNAPSE_MODEL, {"dendritic_delay": .1, "axonal_delay": 6.}),
                                                      (AXONAL_STATIC_SYNAPSE_MODEL, {"dendritic_delay": 2.}),
                                                      (PAIRED_SYNAPSE_MODEL, {"dendritic_delay": 1.5, "axonal_delay": 2.})])
    def test_spike_delivery(self, synapse_model: str, delays: dict):
        r"""Spikes are delivered after the total transmission delay, that is, the sum of the dendritic and axonal delays"""
        self._reset_kernel()

        pre_spike_times = [5., 10., 10.5, 20.]
        total_delay = sum(delays.values())
        w = 2.5

        pre_neuron = self._create_pre_neuron(pre_spike_times)
        if synapse_model == PAIRED_SYNAPSE_MODEL:
            post_neuron = nest.Create(PAIRED_NEURON_MODEL)
            syn_spec = {"synapse_model": synapse_model, "weight": w, "lambda": 0.}     # no plasticity
        else:
            post_neuron = nest.Create(NEURON_MODEL)
            syn_spec = {"synapse_model": synapse_model, "weight": w}

        nest.Connect(pre_neuron, post_neuron, syn_spec={**syn_spec, **delays, "receptor_type": PLASTIC_RECEPTOR})

        mm = nest.Create("multimeter", params={"record_from": ["w_received"], "interval": RESOLUTION})
        nest.Connect(mm, post_neuron)

        nest.Simulate(40.)

        events = mm.get("events")
        np.testing.assert_allclose(events["times"][events["w_received"] != 0.], np.array(pre_spike_times) + total_delay)
        np.testing.assert_allclose(events["w_received"][events["w_received"] != 0.], w)

        conn_status = nest.GetConnections(source=pre_neuron, target=post_neuron).get()
        np.testing.assert_allclose(conn_status["delay"], total_delay)
        if synapse_model != STATIC_SYNAPSE_MODEL:
            np.testing.assert_allclose(conn_status["dendritic_delay"], delays.get("dendritic_delay", 1.))
            np.testing.assert_allclose(conn_status["axonal_delay"], delays.get("axonal_delay", 0.))

    @pytest.mark.parametrize("synapse_model", [AXONAL_STATIC_SYNAPSE_MODEL, PAIRED_SYNAPSE_MODEL])
    def test_axonal_delay_synapse_interface(self, synapse_model: str):
        r"""Synapses with axonal delays take the dendritic and axonal delay, instead of the total delay"""
        self._reset_kernel()

        post_neuron_model = PAIRED_NEURON_MODEL if synapse_model == PAIRED_SYNAPSE_MODEL else NEURON_MODEL
        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(post_neuron_model)

        # the total delay is ambiguous
        with pytest.raises(Exception):
            nest.Connect(pre_neuron, post_neuron, syn_spec={"synapse_model": synapse_model, "delay": 2., "receptor_type": PLASTIC_RECEPTOR})

        with pytest.raises(Exception):
            nest.SetDefaults(synapse_model, {"delay": 2.})

        # the delays can be set using Connect(), SetDefaults() and set()
        nest.SetDefaults(synapse_model, {"axonal_delay": 3.})
        nest.Connect(pre_neuron, post_neuron, syn_spec={"synapse_model": synapse_model, "dendritic_delay": 2., "receptor_type": PLASTIC_RECEPTOR})
        conn = nest.GetConnections(source=pre_neuron, target=post_neuron)
        np.testing.assert_allclose(conn.get("dendritic_delay"), 2.)
        np.testing.assert_allclose(conn.get("axonal_delay"), 3.)
        np.testing.assert_allclose(conn.get("delay"), 5.)

        conn.set({"axonal_delay": 4.})
        np.testing.assert_allclose(conn.get("dendritic_delay"), 2.)
        np.testing.assert_allclose(conn.get("axonal_delay"), 4.)
        np.testing.assert_allclose(conn.get("delay"), 6.)

        with pytest.raises(Exception):
            conn.set({"delay": 1.})

    def test_total_delay_synapse_interface(self):
        r"""Synapses that were not generated with axonal delays take the total delay, which is interpreted as purely dendritic"""
        self._reset_kernel()

        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create(NEURON_MODEL)

        for delay_param in ["axonal_delay", "dendritic_delay"]:
            with pytest.raises(Exception):
                nest.Connect(pre_neuron, post_neuron, syn_spec={"synapse_model": STATIC_SYNAPSE_MODEL, delay_param: 2., "receptor_type": PLASTIC_RECEPTOR})

        nest.Connect(pre_neuron, post_neuron, syn_spec={"synapse_model": STATIC_SYNAPSE_MODEL, "delay": 2., "receptor_type": PLASTIC_RECEPTOR})
        conn = nest.GetConnections(source=pre_neuron, target=post_neuron)
        np.testing.assert_allclose(conn.get("delay"), 2.)

        with pytest.raises(Exception):
            conn.set({"axonal_delay": 1.})

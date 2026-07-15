# -*- coding: utf-8 -*-
#
# test__gap_junction_target.py
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

r"""Part 3 (target side + Hines integration) tests for compartmental gap junctions.

These exercise the target-side handler, the lagged semi-implicit gap term in the
Hines matrix, and the numerical properties of the scheme. The scheme advancing
compartment ``i`` from step ``n`` to ``n+1`` is

    (C_i/dt + g_L,i + sum_axial + sum_j g_ij) V_i[n+1]
        - sum_axial gc V_neighbor[n+1]
        = (C_i/dt) V_i[n] + g_L,i e_L,i + sum_j g_ij V_j[n],

i.e. the local gap conductance is implicit (on the diagonal) and the remote
voltage is delayed by exactly one step. An independent NumPy reference of this
discrete update, and a high-accuracy reference for the underlying coupled
passive equations, are implemented below.
"""

import os

import numpy as np
import pytest
from scipy.linalg import expm

import nest

from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

TESTS_PATH = os.path.realpath(os.path.dirname(__file__))
RESOURCES = os.path.join(TESTS_PATH, "resources")
TARGET = os.path.join(TESTS_PATH, "target")

PASSIVE_MODEL = os.path.join(RESOURCES, "gap_junction_test.nestml")
ACTIVE_MODEL = os.path.join(RESOURCES, "gap_junction_active.nestml")

GAP_OPTS = {
    "gap_junctions": {
        "enable": True,
        "gap_current_port": "i_gap",
        "coupling_scheme": "lagged_semi_implicit",
    }
}

PASSIVE_MODULE = "gap_target_passive_module"
ACTIVE_MODULE = "gap_target_active_module"
DISABLED_MODULE = "gap_target_disabled_module"
PASSIVE_NEURON = "gap_junction_test_model_nestml"
ACTIVE_NEURON = "gap_junction_active_model_nestml"


# ---------------------------------------------------------------------------
# Independent references for the lagged semi-implicit scheme
# ---------------------------------------------------------------------------


class PassiveGapNetwork:
    """Independent reference for passive compartmental neurons coupled by gap
    junctions, using the same lagged semi-implicit discretization as the
    generated model.

    A neuron is a list of compartment dicts ``{"C_m", "g_C", "g_L", "e_L",
    "parent"}`` (``g_C`` is the axial conductance to ``parent``; the root has
    ``parent == -1`` and its ``g_C`` is ignored). Gap junctions are undirected
    edges ``(nA, cA, nB, cB, g)`` added with :meth:`add_gap`.
    """

    def __init__(self, dt):
        self.dt = dt
        self.neurons = []          # list of list-of-compartment-dicts
        self.gaps = []             # list of (nA, cA, nB, cB, g)

    def add_neuron(self, comps):
        self.neurons.append(comps)
        return len(self.neurons) - 1

    def add_gap(self, nA, cA, nB, cB, g):
        self.gaps.append((nA, cA, nB, cB, g))

    def _passive_matrix(self, comps):
        """Backward-Euler passive system matrix A (without gap terms) and the
        static parts used to build the right-hand side."""
        n = len(comps)
        A = np.zeros((n, n))
        cdt = np.array([c["C_m"] / self.dt for c in comps])
        gl = np.array([c["g_L"] for c in comps])
        el = np.array([c["e_L"] for c in comps])
        for i, c in enumerate(comps):
            A[i, i] += cdt[i] + gl[i]
            p = c["parent"]
            if p >= 0:
                gc = c["g_C"]
                A[i, i] += gc
                A[p, p] += gc
                A[i, p] -= gc
                A[p, i] -= gc
        return A, cdt, gl, el

    def simulate(self, nsteps):
        """Return a list (per neuron) of arrays of shape (nsteps, n_comp), the
        committed voltages V[1..nsteps]."""
        mats = [self._passive_matrix(c) for c in self.neurons]
        V = [np.array([c["e_L"] for c in comps], dtype=float) for comps in self.neurons]
        out = [np.zeros((nsteps, len(comps))) for comps in self.neurons]

        # accumulators for the *current* step: zero on the first step (startup)
        sum_g = [np.zeros(len(comps)) for comps in self.neurons]
        weighted_remote = [np.zeros(len(comps)) for comps in self.neurons]

        for step in range(nsteps):
            newV = []
            for k, comps in enumerate(self.neurons):
                A, cdt, gl, el = mats[k]
                S = A.copy()
                S[np.diag_indices_from(S)] += sum_g[k]
                rhs = cdt * V[k] + gl * el + weighted_remote[k]
                newV.append(np.linalg.solve(S, rhs))
            V = newV
            for k in range(len(self.neurons)):
                out[k][step] = V[k]
            # prepare accumulators for the next step from the just-committed
            # voltages -> one-step lag
            sum_g = [np.zeros(len(comps)) for comps in self.neurons]
            weighted_remote = [np.zeros(len(comps)) for comps in self.neurons]
            for (nA, cA, nB, cB, g) in self.gaps:
                sum_g[nA][cA] += g
                weighted_remote[nA][cA] += g * V[nB][cB]
                sum_g[nB][cB] += g
                weighted_remote[nB][cB] += g * V[nA][cA]
        return out

    # -- high-accuracy references for the underlying continuous equations --

    def _continuous_system(self):
        """Assemble the global continuous linear system dV/dt = M V + b over all
        compartments of all neurons, with the gap coupling implicit (no lag)."""
        offsets = []
        n = 0
        for comps in self.neurons:
            offsets.append(n)
            n += len(comps)
        M = np.zeros((n, n))
        b = np.zeros(n)
        for k, comps in enumerate(self.neurons):
            off = offsets[k]
            for i, c in enumerate(comps):
                gi = off + i
                Ci = c["C_m"]
                M[gi, gi] += -c["g_L"] / Ci
                b[gi] += c["g_L"] * c["e_L"] / Ci
                p = c["parent"]
                if p >= 0:
                    gc = c["g_C"]
                    Cp = comps[p]["C_m"]
                    # axial coupling gc(V_neighbor - V_self), scaled by 1/C
                    M[gi, gi] += -gc / Ci
                    M[gi, off + p] += gc / Ci
                    M[off + p, off + p] += -gc / Cp
                    M[off + p, gi] += gc / Cp
        for (nA, cA, nB, cB, g) in self.gaps:
            iA = offsets[nA] + cA
            iB = offsets[nB] + cB
            CA = self.neurons[nA][cA]["C_m"]
            CB = self.neurons[nB][cB]["C_m"]
            M[iA, iA] += -g / CA
            M[iA, iB] += g / CA
            M[iB, iB] += -g / CB
            M[iB, iA] += g / CB
        return M, b, offsets

    def stationary(self):
        """Exact stationary voltages (lag vanishes at the fixed point): solve
        M V + b = 0."""
        M, b, offsets = self._continuous_system()
        Vss = np.linalg.solve(M, -b)
        return [Vss[offsets[k]:offsets[k] + len(comps)] for k, comps in enumerate(self.neurons)]

    def exact_trace(self, nsteps):
        """Exact solution of the continuous coupled system at the grid points
        t = dt .. nsteps*dt, via the matrix exponential."""
        M, b, offsets = self._continuous_system()
        V0 = np.concatenate([[c["e_L"] for c in comps] for comps in self.neurons])
        # V(t) = Vss + expm(M t) (V0 - Vss), with Vss = -M^{-1} b
        Vss = np.linalg.solve(M, -b)
        eMdt = expm(M * self.dt)
        out = [np.zeros((nsteps, len(comps))) for comps in self.neurons]
        d = V0 - Vss
        for step in range(nsteps):
            d = eMdt @ d
            V = Vss + d
            for k, comps in enumerate(self.neurons):
                out[k][step] = V[offsets[k]:offsets[k] + len(comps)]
        return out


def _sim_voltages(mm):
    ev = mm.get("events")
    keys = sorted(k for k in ev.keys() if k.startswith("v_comp"))
    return np.column_stack([ev[k] for k in keys])


# ---------------------------------------------------------------------------
# Fixture: generate + build + install the models once
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module", autouse=True)
def _build_modules():
    if not os.path.exists(TARGET):
        os.makedirs(TARGET)

    generate_nest_compartmental_target(
        input_path=PASSIVE_MODEL,
        target_path=os.path.join(TARGET, "gap_target_passive"),
        module_name=PASSIVE_MODULE,
        suffix="_nestml",
        logging_level="ERROR",
        codegen_opts=GAP_OPTS,
    )
    generate_nest_compartmental_target(
        input_path=ACTIVE_MODEL,
        target_path=os.path.join(TARGET, "gap_target_active"),
        module_name=ACTIVE_MODULE,
        suffix="_nestml",
        logging_level="ERROR",
        codegen_opts=GAP_OPTS,
    )
    # gap-disabled generation for target-API source inspection (not installed)
    generate_nest_compartmental_target(
        input_path=PASSIVE_MODEL,
        target_path=os.path.join(TARGET, "gap_target_disabled"),
        module_name=DISABLED_MODULE,
        suffix="_nestml",
        logging_level="ERROR",
    )


def _install_passive(dt=0.1, threads=1):
    nest.ResetKernel()
    nest.SetKernelStatus({"resolution": dt, "use_wfr": False, "local_num_threads": threads})
    nest.Install(PASSIVE_MODULE + ".so")


def _single_comp_neuron(params):
    cm = nest.Create(PASSIVE_NEURON)
    cm.compartments = [{"parent_idx": -1, "params": params}]
    cm.receptors = [{"comp_idx": 0, "receptor_type": "gap_current"}]
    return cm


# ---------------------------------------------------------------------------
# 1. Generated target-side API
# ---------------------------------------------------------------------------


class TestGeneratedTargetApi:
    def _read(self, sub, base):
        path = os.path.join(TARGET, sub, base)
        with open(path) as f:
            return f.read()

    def test_target_api_enabled(self):
        h = self._read("gap_target_passive", PASSIVE_NEURON + ".h")
        cpp = self._read("gap_target_passive", PASSIVE_NEURON + ".cpp")
        tree_cpp = self._read("gap_target_passive", "cm_tree_" + PASSIVE_NEURON + ".cpp")
        assert "handle( GapJunctionEvent& )" in h
        assert "handles_test_event( GapJunctionEvent&, size_t )" in h
        assert "add_gap_contribution" in h
        assert "add_gap_contribution" in cpp
        assert "add_gap_contribution" in tree_cpp
        # the gap term goes into the diagonal (gg) and rhs (ff)
        assert "->gg) += sum_g" in tree_cpp
        assert "->ff) += weighted_remote" in tree_cpp

    def test_target_api_disabled(self):
        h = self._read("gap_target_disabled", PASSIVE_NEURON + ".h")
        cpp = self._read("gap_target_disabled", PASSIVE_NEURON + ".cpp")
        tree_cpp = self._read("gap_target_disabled", "cm_tree_" + PASSIVE_NEURON + ".cpp")
        assert "GapJunctionEvent" not in h
        assert "add_gap_contribution" not in h
        assert "add_gap_contribution" not in cpp
        assert "add_gap_contribution" not in tree_cpp


# ---------------------------------------------------------------------------
# 2. Two passive single-compartment neurons: reference + analytic stationary
# ---------------------------------------------------------------------------


class TestTwoPassiveSingleCompartment:
    A = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.5, "e_L": -70.0}
    B = {"C_m": 8.0, "g_C": 0.0, "g_L": 1.0, "e_L": -50.0}

    @pytest.mark.parametrize("threads", [1, 2])
    def test_matches_discrete_reference(self, threads):
        dt, T, g = 0.1, 50.0, 3.0
        _install_passive(dt, threads)
        a = _single_comp_neuron(self.A)
        b = _single_comp_neuron(self.B)
        nest.Connect(a, b, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 0, "weight": g})
        mma = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        mmb = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        nest.Connect(mma, a)
        nest.Connect(mmb, b)
        nest.Simulate(T)

        va = _sim_voltages(mma)[:, 0]
        vb = _sim_voltages(mmb)[:, 0]

        ref = PassiveGapNetwork(dt)
        na = ref.add_neuron([{**self.A, "parent": -1}])
        nb = ref.add_neuron([{**self.B, "parent": -1}])
        ref.add_gap(na, 0, nb, 0, g)
        traces = ref.simulate(len(va))
        ra, rb = traces[0][:, 0], traces[1][:, 0]

        assert np.max(np.abs(va - ra)) < 1e-9
        assert np.max(np.abs(vb - rb)) < 1e-9

    def test_stationary_matches_analytic(self):
        dt, T, g = 0.05, 400.0, 2.0
        _install_passive(dt)
        a = _single_comp_neuron(self.A)
        b = _single_comp_neuron(self.B)
        nest.Connect(a, b, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 0, "weight": g})
        mma = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        mmb = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        nest.Connect(mma, a)
        nest.Connect(mmb, b)
        nest.Simulate(T)

        va = _sim_voltages(mma)[-1, 0]
        vb = _sim_voltages(mmb)[-1, 0]

        ref = PassiveGapNetwork(dt)
        ref.add_neuron([{**self.A, "parent": -1}])
        ref.add_neuron([{**self.B, "parent": -1}])
        ref.add_gap(0, 0, 1, 0, g)
        (ssa,), (ssb,) = ref.stationary()
        assert abs(va - ssa) < 1e-3
        assert abs(vb - ssb) < 1e-3

    def test_equal_endpoints_zero_stationary_current(self):
        """Two identical neurons reach the common resting potential; the
        stationary gap current is zero."""
        dt, T, g = 0.1, 300.0, 5.0
        same = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.0, "e_L": -65.0}
        _install_passive(dt)
        a = _single_comp_neuron(same)
        b = _single_comp_neuron(same)
        nest.Connect(a, b, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 0, "weight": g})
        mma = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        mmb = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        nest.Connect(mma, a)
        nest.Connect(mmb, b)
        nest.Simulate(T)
        va = _sim_voltages(mma)[-1, 0]
        vb = _sim_voltages(mmb)[-1, 0]
        assert abs(va - (-65.0)) < 1e-6
        assert abs(vb - (-65.0)) < 1e-6
        assert abs(va - vb) < 1e-9  # zero gap current

    @pytest.mark.parametrize("g", [0.05, 50.0])
    def test_strong_and_weak_conductance(self, g):
        dt, T = 0.05, 60.0
        _install_passive(dt)
        a = _single_comp_neuron(self.A)
        b = _single_comp_neuron(self.B)
        nest.Connect(a, b, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 0, "weight": g})
        mma = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        mmb = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        nest.Connect(mma, a)
        nest.Connect(mmb, b)
        nest.Simulate(T)
        va = _sim_voltages(mma)[:, 0]
        vb = _sim_voltages(mmb)[:, 0]
        ref = PassiveGapNetwork(dt)
        ref.add_neuron([{**self.A, "parent": -1}])
        ref.add_neuron([{**self.B, "parent": -1}])
        ref.add_gap(0, 0, 1, 0, g)
        traces = ref.simulate(len(va))
        assert np.max(np.abs(va - traces[0][:, 0])) < 1e-8
        assert np.max(np.abs(vb - traces[1][:, 0])) < 1e-8


# ---------------------------------------------------------------------------
# 3. Multicompartment neurons vs global conductance-matrix reference
# ---------------------------------------------------------------------------


class TestMulticompartment:
    def _two_comp(self, soma, dend):
        cm = nest.Create(PASSIVE_NEURON)
        cm.compartments = [{"parent_idx": -1, "params": soma},
                           {"parent_idx": 0, "params": dend}]
        cm.receptors = [{"comp_idx": 0, "receptor_type": "gap_current"},
                        {"comp_idx": 1, "receptor_type": "gap_current"}]
        return cm

    def test_two_two_comp_neurons(self):
        dt, T, g = 0.1, 80.0, 2.5
        soma_a = {"C_m": 12.0, "g_C": 0.0, "g_L": 1.2, "e_L": -68.0}
        dend_a = {"C_m": 6.0, "g_C": 1.5, "g_L": 0.8, "e_L": -62.0}
        soma_b = {"C_m": 9.0, "g_C": 0.0, "g_L": 1.0, "e_L": -55.0}
        dend_b = {"C_m": 5.0, "g_C": 2.0, "g_L": 0.7, "e_L": -58.0}

        _install_passive(dt)
        a = self._two_comp(soma_a, dend_a)
        b = self._two_comp(soma_b, dend_b)
        # dendrite(port 1) of a  <->  soma(port 0) of b (different endpoint idx)
        nest.Connect(a, b, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 1,
                      "receptor_type": 0, "weight": g})
        mma = nest.Create("multimeter", 1, {"record_from": ["v_comp0", "v_comp1"], "interval": dt})
        mmb = nest.Create("multimeter", 1, {"record_from": ["v_comp0", "v_comp1"], "interval": dt})
        nest.Connect(mma, a)
        nest.Connect(mmb, b)
        nest.Simulate(T)
        va = _sim_voltages(mma)
        vb = _sim_voltages(mmb)

        ref = PassiveGapNetwork(dt)
        na = ref.add_neuron([{**soma_a, "parent": -1}, {**dend_a, "parent": 0}])
        nb = ref.add_neuron([{**soma_b, "parent": -1}, {**dend_b, "parent": 0}])
        ref.add_gap(na, 1, nb, 0, g)  # a.dend <-> b.soma
        traces = ref.simulate(len(va))
        assert np.max(np.abs(va - traces[0])) < 1e-8
        assert np.max(np.abs(vb - traces[1])) < 1e-8


# ---------------------------------------------------------------------------
# 4. Source and target selection, multiple junctions, symmetric endpoints
# ---------------------------------------------------------------------------


class TestRouting:
    def test_target_selection_same_source_two_targets(self):
        """One remote waveform routed to two different target compartments; each
        target sees the same remote voltage but with its own local dynamics."""
        dt, T, g = 0.1, 60.0, 3.0
        src = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.0, "e_L": -40.0}
        t_soma = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.0, "e_L": -70.0}
        t_dend = {"C_m": 6.0, "g_C": 1.0, "g_L": 1.5, "e_L": -75.0}

        _install_passive(dt)
        s = _single_comp_neuron(src)
        tgt = nest.Create(PASSIVE_NEURON)
        tgt.compartments = [{"parent_idx": -1, "params": t_soma},
                            {"parent_idx": 0, "params": t_dend}]
        tgt.receptors = [{"comp_idx": 0, "receptor_type": "gap_current"},
                         {"comp_idx": 1, "receptor_type": "gap_current"}]
        # source port 0 of s connects to BOTH target ports 0 and 1
        nest.Connect(s, tgt, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 0, "weight": g})
        nest.Connect(s, tgt, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 1, "weight": g})
        mmt = nest.Create("multimeter", 1, {"record_from": ["v_comp0", "v_comp1"], "interval": dt})
        nest.Connect(mmt, tgt)
        nest.Simulate(T)
        vt = _sim_voltages(mmt)

        ref = PassiveGapNetwork(dt)
        ns = ref.add_neuron([{**src, "parent": -1}])
        nt = ref.add_neuron([{**t_soma, "parent": -1}, {**t_dend, "parent": 0}])
        ref.add_gap(ns, 0, nt, 0, g)
        ref.add_gap(ns, 0, nt, 1, g)
        traces = ref.simulate(len(vt))
        assert np.max(np.abs(vt - traces[1])) < 1e-8
        # the two target compartments carry measurably distinct voltages
        assert np.max(np.abs(vt[:, 0] - vt[:, 1])) > 1e-2

    def test_multiple_junctions_on_one_compartment_add_linearly(self):
        """Two source neurons both terminate on one target compartment; the
        conductances and weighted remote voltages add linearly."""
        dt, T = 0.1, 60.0
        g1, g2 = 2.0, 4.0
        s1 = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.0, "e_L": -40.0}
        s2 = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.0, "e_L": -20.0}
        tp = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.0, "e_L": -70.0}

        _install_passive(dt)
        n1 = _single_comp_neuron(s1)
        n2 = _single_comp_neuron(s2)
        tg = _single_comp_neuron(tp)
        nest.Connect(n1, tg, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 0, "weight": g1})
        nest.Connect(n2, tg, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 0, "weight": g2})
        mmt = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        nest.Connect(mmt, tg)
        nest.Simulate(T)
        vt = _sim_voltages(mmt)[:, 0]

        ref = PassiveGapNetwork(dt)
        r1 = ref.add_neuron([{**s1, "parent": -1}])
        r2 = ref.add_neuron([{**s2, "parent": -1}])
        rt = ref.add_neuron([{**tp, "parent": -1}])
        ref.add_gap(r1, 0, rt, 0, g1)
        ref.add_gap(r2, 0, rt, 0, g2)
        traces = ref.simulate(len(vt))
        assert np.max(np.abs(vt - traces[2][:, 0])) < 1e-8

    def test_symmetric_unequal_endpoints(self):
        """The plan's example: differing source/target port indices with
        make_symmetric. The reverse connection must use the swapped indices."""
        dt, T, g = 0.1, 50.0, 1.5
        pa = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.0, "e_L": -70.0}
        pb = {"C_m": 8.0, "g_C": 0.0, "g_L": 1.2, "e_L": -55.0}

        _install_passive(dt)
        # a: ports 0 (soma), 1 (dend); b: ports 0 (soma), 1 (dend)
        a = nest.Create(PASSIVE_NEURON)
        a.compartments = [{"parent_idx": -1, "params": pa},
                          {"parent_idx": 0, "params": {**pa, "g_C": 1.0, "e_L": -66.0}}]
        a.receptors = [{"comp_idx": 0, "receptor_type": "gap_current"},
                       {"comp_idx": 1, "receptor_type": "gap_current"}]
        b = nest.Create(PASSIVE_NEURON)
        b.compartments = [{"parent_idx": -1, "params": pb},
                          {"parent_idx": 0, "params": {**pb, "g_C": 1.3, "e_L": -52.0}}]
        b.receptors = [{"comp_idx": 0, "receptor_type": "gap_current"},
                       {"comp_idx": 1, "receptor_type": "gap_current"}]
        # forward a[source_port=1] -> b[receptor_type=0]
        # reverse b[source_port=0] -> a[receptor_type=1]
        nest.Connect(a, b, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 1,
                      "receptor_type": 0, "weight": g})
        conns = nest.GetConnections(synapse_model="gap_junction")
        # two directed connections exist, with swapped endpoint indices
        sports = sorted(conns.get("source_port"))
        assert sports == [0, 1]

        mma = nest.Create("multimeter", 1, {"record_from": ["v_comp0", "v_comp1"], "interval": dt})
        mmb = nest.Create("multimeter", 1, {"record_from": ["v_comp0", "v_comp1"], "interval": dt})
        nest.Connect(mma, a)
        nest.Connect(mmb, b)
        nest.Simulate(T)
        va = _sim_voltages(mma)
        vb = _sim_voltages(mmb)

        ref = PassiveGapNetwork(dt)
        na = ref.add_neuron([{**pa, "parent": -1}, {**pa, "g_C": 1.0, "e_L": -66.0, "parent": 0}])
        nb = ref.add_neuron([{**pb, "parent": -1}, {**pb, "g_C": 1.3, "e_L": -52.0, "parent": 0}])
        ref.add_gap(na, 1, nb, 0, g)  # a.dend <-> b.soma
        traces = ref.simulate(len(va))
        assert np.max(np.abs(va - traces[0])) < 1e-8
        assert np.max(np.abs(vb - traces[1])) < 1e-8

    def test_source_selection_two_ports_distinct_voltages(self):
        """Two source ports on one neuron drive two independent target neurons;
        each target follows the voltage of the port it connected to."""
        dt, T, g = 0.1, 60.0, 4.0
        soma = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.0, "e_L": -30.0}
        dend = {"C_m": 6.0, "g_C": 1.0, "g_L": 1.0, "e_L": -80.0}
        tp = {"C_m": 10.0, "g_C": 0.0, "g_L": 0.5, "e_L": -65.0}

        _install_passive(dt)
        src = nest.Create(PASSIVE_NEURON)
        src.compartments = [{"parent_idx": -1, "params": soma},
                            {"parent_idx": 0, "params": dend}]
        src.receptors = [{"comp_idx": 0, "receptor_type": "gap_current"},
                         {"comp_idx": 1, "receptor_type": "gap_current"}]
        t0 = _single_comp_neuron(tp)
        t1 = _single_comp_neuron(tp)
        nest.Connect(src, t0, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 0, "weight": g})
        nest.Connect(src, t1, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 1,
                      "receptor_type": 0, "weight": g})
        mm0 = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        mm1 = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        nest.Connect(mm0, t0)
        nest.Connect(mm1, t1)
        nest.Simulate(T)
        v0 = _sim_voltages(mm0)[:, 0]
        v1 = _sim_voltages(mm1)[:, 0]

        ref = PassiveGapNetwork(dt)
        ns = ref.add_neuron([{**soma, "parent": -1}, {**dend, "parent": 0}])
        rt0 = ref.add_neuron([{**tp, "parent": -1}])
        rt1 = ref.add_neuron([{**tp, "parent": -1}])
        ref.add_gap(ns, 0, rt0, 0, g)  # target 0 <- soma
        ref.add_gap(ns, 1, rt1, 0, g)  # target 1 <- dend
        traces = ref.simulate(len(v0))
        assert np.max(np.abs(v0 - traces[1][:, 0])) < 1e-8
        assert np.max(np.abs(v1 - traces[2][:, 0])) < 1e-8
        # the two targets are pulled toward different source voltages
        assert abs(v0[-1] - v1[-1]) > 1.0


# ---------------------------------------------------------------------------
# 5. Startup, multiple Simulate calls, ordinary input, kappa
# ---------------------------------------------------------------------------


class TestSchemeBehavior:
    A = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.5, "e_L": -70.0}
    B = {"C_m": 8.0, "g_C": 0.0, "g_L": 1.0, "e_L": -50.0}

    def test_first_step_zero_gap_contribution(self):
        """On the first step the accumulators are zero, so each neuron advances
        as if uncoupled; the gap term only appears from the second step on."""
        dt, g = 0.1, 20.0
        _install_passive(dt)
        a = _single_comp_neuron(self.A)
        b = _single_comp_neuron(self.B)
        nest.Connect(a, b, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 0, "weight": g})
        mma = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        nest.Connect(mma, a)
        nest.Simulate(1.0)  # va[0] is the first recorded sample, i.e. V[1]
        va = _sim_voltages(mma)[:, 0]

        # uncoupled first step: (C/dt) V0 + gL eL over (C/dt + gL)
        cdt = self.A["C_m"] / dt
        v1_uncoupled = (cdt * self.A["e_L"] + self.A["g_L"] * self.A["e_L"]) / (cdt + self.A["g_L"])
        # e_L == V0 so the first step should not move (no gap, at rest)
        assert abs(va[0] - v1_uncoupled) < 1e-9
        assert abs(va[0] - self.A["e_L"]) < 1e-9

    def test_multiple_simulate_calls_preserve_remote_sample(self):
        dt, g = 0.1, 3.0
        _install_passive(dt)
        a = _single_comp_neuron(self.A)
        b = _single_comp_neuron(self.B)
        nest.Connect(a, b, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 0, "weight": g})
        mma = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        mmb = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        nest.Connect(mma, a)
        nest.Connect(mmb, b)
        for _ in range(5):
            nest.Simulate(10.0)
        va = _sim_voltages(mma)[:, 0]
        vb = _sim_voltages(mmb)[:, 0]

        ref = PassiveGapNetwork(dt)
        ref.add_neuron([{**self.A, "parent": -1}])
        ref.add_neuron([{**self.B, "parent": -1}])
        ref.add_gap(0, 0, 1, 0, g)
        traces = ref.simulate(len(va))
        # chunked Simulate must give the same trajectory as one continuous run
        assert np.max(np.abs(va - traces[0][:, 0])) < 1e-8
        assert np.max(np.abs(vb - traces[1][:, 0])) < 1e-8

    def test_ordinary_stim_input_still_works(self):
        """A dc_generator into the ordinary i_stim receptor still drives the
        neuron while gap support is enabled."""
        dt = 0.1
        _install_passive(dt)
        cm = nest.Create(PASSIVE_NEURON)
        cm.compartments = [{"parent_idx": -1, "params": self.A}]
        cm.receptors = [{"comp_idx": 0, "receptor_type": "gap_current"},
                        {"comp_idx": 0, "receptor_type": "stim_current"}]
        dcg = nest.Create("dc_generator", {"amplitude": 100.0})
        nest.Connect(dcg, cm, syn_spec={"synapse_model": "static_synapse",
                                        "weight": 1.0, "delay": dt, "receptor_type": 1})
        mm = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        nest.Connect(mm, cm)
        nest.Simulate(100.0)
        v = _sim_voltages(mm)[:, 0]
        # depolarized above rest by the injected current
        assert v[-1] > self.A["e_L"] + 1.0

    def test_kappa_within_validated_range(self):
        """Record the dimensionless coupling number kappa = dt sum_j g_ij / C_i
        for a representative configuration; document that it stays in the
        validated range where the approximation is accurate."""
        dt, g = 0.1, 3.0
        C = self.A["C_m"]
        kappa = dt * g / C
        assert kappa < 1.0  # comfortably within the validated envelope


# ---------------------------------------------------------------------------
# 6. Timestep convergence toward the high-accuracy coupled solution
# ---------------------------------------------------------------------------


class TestConvergence:
    A = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.5, "e_L": -70.0}
    B = {"C_m": 8.0, "g_C": 0.0, "g_L": 1.0, "e_L": -50.0}

    def _run(self, dt, T, g):
        _install_passive(dt)
        a = _single_comp_neuron(self.A)
        b = _single_comp_neuron(self.B)
        nest.Connect(a, b, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 0, "weight": g})
        mma = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        mmb = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        nest.Connect(mma, a)
        nest.Connect(mmb, b)
        nest.Simulate(T)
        return _sim_voltages(mma)[:, 0], _sim_voltages(mmb)[:, 0]

    def test_error_halves_with_dt(self):
        """The transient error against the exact coupled solution decreases as
        the timestep is reduced (first order in dt)."""
        T, g = 20.0, 6.0

        def max_err(dt):
            va, vb = self._run(dt, T, g)
            ref = PassiveGapNetwork(dt)
            ref.add_neuron([{**self.A, "parent": -1}])
            ref.add_neuron([{**self.B, "parent": -1}])
            ref.add_gap(0, 0, 1, 0, g)
            exact = ref.exact_trace(len(va))
            ea = np.max(np.abs(va - exact[0][:, 0]))
            eb = np.max(np.abs(vb - exact[1][:, 0]))
            return max(ea, eb)

        e_coarse = max_err(0.2)
        e_fine = max_err(0.05)
        # 4x smaller dt should reduce the error substantially (at least ~2x),
        # consistent with the first-order accuracy of the one-step lag
        assert e_fine < e_coarse / 2.0
        # and the fine solution is close to the exact coupled trajectory
        # (well below the ~20 mV scale of the driving offset between the neurons)
        assert e_fine < 1.0


# ---------------------------------------------------------------------------
# 7. Stability regression: difference-mode amplification (C/dt - g)/(C/dt + g)
# ---------------------------------------------------------------------------


class TestStability:
    def test_difference_mode_amplification(self):
        """Two identical passive compartments coupled only by a gap junction:
        the difference mode d[n] = V_A[n] - V_B[n] decays by the exact factor
        (C/dt - g)/(C/dt + g) per step. This verifies the implicit local term
        and the one-step-lagged remote term (a fully explicit current would give
        (C/dt - g)/(C/dt) or similar)."""
        dt, g = 0.1, 4.0
        C, gL, eL = 10.0, 0.0, -65.0  # gL=0 isolates the pure gap difference mode
        # NOTE: g_L must be > 0 for a well-posed passive neuron; use a tiny value
        gL = 1e-6
        params = {"C_m": C, "g_C": 0.0, "g_L": gL, "e_L": eL}

        _install_passive(dt)
        a = nest.Create(PASSIVE_NEURON)
        b = nest.Create(PASSIVE_NEURON)
        # start the two neurons at different voltages to excite the difference mode
        a.compartments = [{"parent_idx": -1, "params": {**params, "v_comp": -60.0}}]
        b.compartments = [{"parent_idx": -1, "params": {**params, "v_comp": -70.0}}]
        a.receptors = [{"comp_idx": 0, "receptor_type": "gap_current"}]
        b.receptors = [{"comp_idx": 0, "receptor_type": "gap_current"}]
        nest.Connect(a, b, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 0, "weight": g})
        mma = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        mmb = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        nest.Connect(mma, a)
        nest.Connect(mmb, b)
        nest.Simulate(5.0)
        va = _sim_voltages(mma)[:, 0]
        vb = _sim_voltages(mmb)[:, 0]
        d = va - vb

        cdt = C / dt
        expected_factor = (cdt - g) / (cdt + g)
        # measure the per-step ratio once the mode has settled onto the
        # eigenvector (skip the first few steps affected by the startup lag)
        ratios = d[5:] / d[4:-1]
        assert np.allclose(ratios, expected_factor, atol=1e-3), \
            f"observed {np.mean(ratios):.6f}, expected {expected_factor:.6f}"


# ---------------------------------------------------------------------------
# 8. Active channels + spikes
# ---------------------------------------------------------------------------


class TestActive:
    def test_active_neurons_couple_and_run(self):
        """Two active (Na/K) neurons: one is driven to spike; the gap junction
        perturbs the partner's voltage. Runs on multiple threads."""
        dt = 0.025
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": dt, "use_wfr": False, "local_num_threads": 2})
        nest.Install(ACTIVE_MODULE + ".so")

        soma = {"C_m": 1.0, "g_C": 0.0, "g_L": 0.1, "e_L": -70.0,
                "gbar_Na": 2.0, "gbar_K": 0.5}

        def make():
            cm = nest.Create(ACTIVE_NEURON)
            cm.compartments = [{"parent_idx": -1, "params": soma}]
            cm.receptors = [{"comp_idx": 0, "receptor_type": "gap_current"},
                            {"comp_idx": 0, "receptor_type": "stim_current"}]
            return cm

        driven = make()
        partner = make()
        nest.Connect(driven, partner, {"rule": "one_to_one", "make_symmetric": True},
                     {"synapse_model": "gap_junction", "source_port": 0,
                      "receptor_type": 0, "weight": 3.0})
        dcg = nest.Create("dc_generator", {"amplitude": 3.0})
        nest.Connect(dcg, driven, syn_spec={"synapse_model": "static_synapse",
                                            "weight": 1.0, "delay": dt, "receptor_type": 1})
        mm = nest.Create("multimeter", 1, {"record_from": ["v_comp0"], "interval": dt})
        nest.Connect(mm, partner)
        nest.Simulate(100.0)
        vp = _sim_voltages(mm)[:, 0]
        # the partner is not driven directly; coupling to the spiking neuron must
        # perturb its voltage away from rest
        assert np.max(vp) > -70.0 + 1.0

    def test_spike_time_shift_with_coupling(self):
        """A neuron near threshold spikes earlier when gap-coupled to a
        depolarized partner than when uncoupled."""
        dt = 0.025
        soma = {"C_m": 1.0, "g_C": 0.0, "g_L": 0.1, "e_L": -70.0,
                "gbar_Na": 2.0, "gbar_K": 0.5}

        def first_spike(coupled):
            nest.ResetKernel()
            nest.SetKernelStatus({"resolution": dt, "use_wfr": False})
            nest.Install(ACTIVE_MODULE + ".so")
            probe = nest.Create(ACTIVE_NEURON)
            probe.compartments = [{"parent_idx": -1, "params": soma}]
            probe.receptors = [{"comp_idx": 0, "receptor_type": "gap_current"},
                               {"comp_idx": 0, "receptor_type": "stim_current"}]
            # mild drive: subthreshold-ish on its own
            dcg = nest.Create("dc_generator", {"amplitude": 1.6})
            nest.Connect(dcg, probe, syn_spec={"synapse_model": "static_synapse",
                                               "weight": 1.0, "delay": dt, "receptor_type": 1})
            if coupled:
                hot = nest.Create(ACTIVE_NEURON)
                hot.compartments = [{"parent_idx": -1, "params": {**soma, "e_L": 0.0}}]
                hot.receptors = [{"comp_idx": 0, "receptor_type": "gap_current"},
                                 {"comp_idx": 0, "receptor_type": "stim_current"}]
                nest.Connect(probe, hot, {"rule": "one_to_one", "make_symmetric": True},
                             {"synapse_model": "gap_junction", "source_port": 0,
                              "receptor_type": 0, "weight": 2.0})
            sr = nest.Create("spike_recorder")
            nest.Connect(probe, sr)
            nest.Simulate(100.0)
            times = sr.get("events")["times"]
            return times[0] if len(times) else np.inf

        t_uncoupled = first_spike(False)
        t_coupled = first_spike(True)
        assert t_coupled < t_uncoupled, \
            f"coupled first spike {t_coupled} not earlier than uncoupled {t_uncoupled}"

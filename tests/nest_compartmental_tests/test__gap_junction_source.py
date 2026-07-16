# -*- coding: utf-8 -*-
#
# test__gap_junction_source.py
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

r"""Part 2 (source side) tests for compartmental gap junctions.

These exercise the source-side code generation: generator-option validation, the
opt-out of waveform relaxation, the electrical port map, one-scalar-per-step
secondary-event emission, and the ordinary-input behavior of the designated gap
mechanism. The target side and the numerical reference are covered in Part 3.
"""

import glob
import os

import pytest

import nest

from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

TESTS_PATH = os.path.realpath(os.path.dirname(__file__))
RESOURCES = os.path.join(TESTS_PATH, "resources")
TARGET = os.path.join(TESTS_PATH, "target")

MODEL = os.path.join(RESOURCES, "gap_junction_test.nestml")
NOGAP_MODEL = os.path.join(RESOURCES, "gap_junction_nogap.nestml")

ENABLED_MODULE = "gap_source_enabled_module"
DISABLED_MODULE = "gap_source_disabled_module"
NEURON = "gap_junction_test_model_nestml"
NOGAP_NEURON = "gap_junction_nogap_model_nestml"


def _read_generated(target_dir, basename):
    path = os.path.join(target_dir, basename)
    assert os.path.exists(path), f"generated file not found: {path}"
    with open(path) as f:
        return f.read()


def _make_neuron():
    """Two-compartment neuron with interleaved gap/AMPA/gap/stim receptors.

    Port (index into cm.receptors) -> receptor:
      0 gap_current  (soma, comp 0)
      1 AMPA         (soma, comp 0)
      2 gap_current  (dendrite, comp 1)
      3 stim_current (soma, comp 0)
    """
    cm = nest.Create(NEURON)
    soma = {"C_m": 10.0, "g_C": 0.0, "g_L": 1.5, "e_L": -70.0}
    dend = {"C_m": 5.0, "g_C": 2.0, "g_L": 1.0, "e_L": -60.0}
    cm.compartments = [
        {"parent_idx": -1, "params": soma},
        {"parent_idx": 0, "params": dend},
    ]
    cm.receptors = [
        {"comp_idx": 0, "receptor_type": "gap_current"},
        {"comp_idx": 0, "receptor_type": "AMPA"},
        {"comp_idx": 1, "receptor_type": "gap_current"},
        {"comp_idx": 0, "receptor_type": "stim_current"},
    ]
    return cm


class TestGapJunctionSourceValidation:
    """Validation of the @mechanism::gap designation. Each case must fail during
    code generation, before any C++ is compiled."""

    @pytest.mark.parametrize(
        "model, needle",
        [
            # a gap mechanism whose current port has non-current units
            ("gap_junction_bad_unit.nestml",
             "not compatible with an electrical current"),
            # two @mechanism::gap mechanisms -> ambiguous designation
            ("gap_junction_ambiguous.nestml",
             "more than one @mechanism::gap mechanism"),
        ],
    )
    def test_validation_rejects(self, model, needle):
        with pytest.raises(Exception) as excinfo:
            generate_nest_compartmental_target(
                input_path=os.path.join(RESOURCES, model),
                target_path=os.path.join(TARGET, "gap_validation"),
                module_name="gap_validation_module",
                suffix="_nestml",
                logging_level="ERROR",
            )
        assert needle in str(excinfo.value)


class TestGapJunctionSource:
    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        if not os.path.exists(TARGET):
            os.makedirs(TARGET)

        # gap-enabled: the model uses @mechanism::gap, so no options are needed
        generate_nest_compartmental_target(
            input_path=MODEL,
            target_path=os.path.join(TARGET, "gap_enabled"),
            module_name=ENABLED_MODULE,
            suffix="_nestml",
            logging_level="ERROR",
        )

        # gap-disabled: a structurally identical model without a gap mechanism
        # (i_gap is an ordinary continuous input). Generated for source-code
        # inspection; not installed.
        generate_nest_compartmental_target(
            input_path=NOGAP_MODEL,
            target_path=os.path.join(TARGET, "gap_disabled"),
            module_name=DISABLED_MODULE,
            suffix="_nestml",
            logging_level="ERROR",
        )

    # ---- generated-code structure ----

    def test_generated_source_api_enabled(self):
        target = os.path.join(TARGET, "gap_enabled")
        h = _read_generated(target, NEURON + ".h")
        cpp = _read_generated(target, NEURON + ".cpp")

        assert "sends_secondary_event( GapJunctionEvent&, const size_t" in h
        assert "gap_port_comp_" in h
        assert "send_secondary( *this, ge" in cpp
        assert "set_node_uses_wfr( false )" in cpp
        # no waveform-relaxation implementation is generated in this scheme
        assert "wfr_update" not in h
        assert "wfr_update" not in cpp

    def test_generated_source_api_disabled(self):
        target = os.path.join(TARGET, "gap_disabled")
        h = _read_generated(target, NOGAP_NEURON + ".h")
        cpp = _read_generated(target, NOGAP_NEURON + ".cpp")

        # gap support disabled: no secondary-event API and no gap machinery
        assert "GapJunctionEvent" not in h
        assert "sends_secondary_event" not in h
        assert "gap_port_comp_" not in h
        assert "send_secondary" not in cpp
        assert "set_node_uses_wfr" not in cpp
        assert "wfr_update" not in h and "wfr_update" not in cpp

    # ---- runtime behavior ----

    def test_lone_simulation_distinct_compartment_voltages(self):
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": 0.1, "use_wfr": False})
        nest.Install(ENABLED_MODULE + ".so")

        cm = _make_neuron()
        mm = nest.Create("multimeter", 1, {"record_from": ["v_comp0", "v_comp1"], "interval": 0.1})
        nest.Connect(mm, cm)
        nest.Simulate(50.0)

        ev = nest.GetStatus(mm, "events")[0]
        # the two gap source ports sit on compartments with different e_L, so
        # they carry measurably different voltages -> two distinct samples
        assert abs(ev["v_comp0"][-1] - ev["v_comp1"][-1]) > 1e-2

    def test_port_map_current_event_behavior(self):
        """The designated gap mechanism does not consume CurrentEvent values; a
        continuous current addressed to a gap-only receptor is rejected, while an
        ordinary continuous receptor still accepts it."""
        # CurrentEvent to a gap receptor (port 0) is rejected
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": 0.1, "use_wfr": False})
        nest.Install(ENABLED_MODULE + ".so")
        cm = _make_neuron()
        dcg = nest.Create("dc_generator", {"amplitude": 5.0})
        nest.Connect(dcg, cm, syn_spec={"synapse_model": "static_synapse",
                                        "weight": 1.0, "delay": 0.1, "receptor_type": 0})
        with pytest.raises(Exception):
            nest.Simulate(5.0)

        # CurrentEvent to the ordinary stim receptor (port 3) is accepted
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": 0.1, "use_wfr": False})
        nest.Install(ENABLED_MODULE + ".so")
        cm = _make_neuron()
        dcg = nest.Create("dc_generator", {"amplitude": 5.0})
        nest.Connect(dcg, cm, syn_spec={"synapse_model": "static_synapse",
                                        "weight": 1.0, "delay": 0.1, "receptor_type": 3})
        nest.Simulate(5.0)  # must not raise

    def test_source_port_validation(self):
        """Only receptors that are instances of the designated gap mechanism are
        valid electrical source ports.

        A gap connection must be symmetric, but the compartmental target handler
        arrives in Part 3, so the reverse pass fails and (by NEST's connection
        semantics) masks the forward-pass error. We therefore verify the
        source-side validation directly: the forward connection is created iff
        ``sends_secondary_event`` accepted the source port.
        """
        for port, valid in [(0, True), (2, True), (1, False), (3, False), (99, False)]:
            nest.ResetKernel()
            nest.SetKernelStatus({"resolution": 0.1, "use_wfr": False})
            nest.Install(ENABLED_MODULE + ".so")
            cm = _make_neuron()
            tgt = nest.Create("hh_psc_alpha_gap")
            try:
                nest.Connect(cm, tgt, {"rule": "one_to_one", "make_symmetric": True},
                             {"synapse_model": "gap_junction", "source_port": port, "weight": 1.0})
            except Exception:
                pass
            n_forward = len(nest.GetConnections(source=cm, synapse_model="gap_junction"))
            assert (n_forward == 1) == valid, f"source_port {port}: expected valid={valid}"

    def test_comm_interval_rejection(self):
        """Secondary events must be exchanged every resolution step; a coarser
        waveform-relaxation communication interval is rejected before simulation."""
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": 0.1, "use_wfr": True, "wfr_comm_interval": 2.0})
        nest.Install(ENABLED_MODULE + ".so")
        cm = _make_neuron()
        with pytest.raises(Exception):
            nest.Simulate(5.0)

    def test_per_step_communication_accepted(self):
        """use_wfr=False forces the communication interval to the resolution and
        is accepted."""
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": 0.1, "use_wfr": False})
        nest.Install(ENABLED_MODULE + ".so")
        cm = _make_neuron()
        nest.Simulate(5.0)  # must not raise

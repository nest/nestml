# -*- coding: utf-8 -*-
#
# test_precompute_reciprocals.py
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
import re

import numpy as np
import pytest

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.transformers.precompute_reciprocals_transformer import PrecomputeReciprocalsTransformer
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor


def get_propagator_assignments(target_path: str, model_name: str):
    r"""Return all lines of generated code for the given model in which a propagator is assigned a value."""
    lines = []
    for ext in ["cpp", "h"]:
        fn = os.path.join(target_path, model_name + "." + ext)
        if os.path.exists(fn):
            with open(fn) as f:
                lines.extend([line.strip() for line in f if re.search(r"__P__\w+\s*=[^=]", line)])

    return lines


def get_denominators(line: str):
    r"""Return the denominators of all divisions in a line of generated C++ code. A denominator is either a parenthesised expression, or a single term (such as ``P_.tau_m`` or ``std::exp(...)``)."""
    rhs = line.split("=", 1)[1].split("//")[0]
    denominators = []
    for match in re.finditer(r"/", rhs):
        i = match.end()
        while i < len(rhs) and rhs[i] == " ":
            i += 1

        start = i
        # term: identifier (possibly with namespace and member access), optionally followed by a parenthesised argument list
        m = re.match(r"[\w.:]*", rhs[i:])
        i += m.end()
        if i < len(rhs) and rhs[i] == "(":
            depth = 0
            while i < len(rhs):
                depth += {"(": 1, ")": -1}.get(rhs[i], 0)
                i += 1
                if depth == 0:
                    break

        denominators.append(rhs[start:i])

    return denominators


def is_constant_denominator(denominator: str) -> bool:
    r"""Return True if the denominator only depends on parameters (``P_.``) and numeric literals."""
    without_parameters = re.sub(r"P_\.\w+", "", denominator)
    return "P_." in denominator and re.fullmatch(r"[\d.eE\s()+\-*]*", without_parameters) is not None


def get_divisions_by_constants(target_path: str, model_name: str):
    r"""Return the denominators of all divisions by constants (expressions that only depend on parameters) in the propagators of the given model."""
    propagator_assignments = get_propagator_assignments(target_path, model_name)
    assert propagator_assignments, "No propagators found for model " + model_name + " in " + target_path

    return [denominator for line in propagator_assignments for denominator in get_denominators(line) if is_constant_denominator(denominator)]


def check_generated_code(target_path_ref: str, model_name_ref: str, target_path: str, model_name: str):
    # the reference code should contain divisions by constants, e.g. "/ P_.tau_m" or "/ (P_.C_m * (P_.tau_m - P_.tau_syn_exc))"...
    assert get_divisions_by_constants(target_path_ref, model_name_ref), "Expected divisions by parameters in the propagators in the reference code"

    # ...but after the transformation, there should be none left (divisions by expressions that depend on ``__h`` are left as they are)
    assert get_divisions_by_constants(target_path, model_name) == []

    assert any("__inv_" in line for line in get_propagator_assignments(target_path, model_name))


class TestPrecomputeReciprocalsTransformer:
    r"""Test the transformer directly on the AST of a model, with propagators of the kind that ODE-toolbox produces."""

    model_src = """model test_model:
    state:
        x real = 0

    parameters:
        tau ms = 20 ms
        tau_a ms = 2 ms
        tau_b ms = 10 ms
        C_m pF = 250 pF

    internals:
        __h ms = resolution()
        __P__x__x real = exp(-__h / tau)
        __P__x__y real = tau_a * tau_b * (exp(-__h / tau_a) - exp(-__h / tau_b)) / (C_m * (tau_a - tau_b))
        __P__y__y real = 1 / tau + x / __h + 3 / (tau)
"""

    @pytest.fixture(scope="class", autouse=True)
    def setUp(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
        PredefinedUnits.register_units()
        PredefinedTypes.register_types()
        PredefinedVariables.register_variables()
        PredefinedFunctions.register_functions()
        Logger.init_logger(LoggingLevel.INFO)

    def _transform(self, options=None):
        model = ModelParser.parse_model(self.model_src)
        model.accept(ASTSymbolTableVisitor())
        metadata = {}
        PrecomputeReciprocalsTransformer(options).transform([model], metadata)
        internals = {decl.get_variables()[0].get_name(): str(decl.get_expression()).replace(" ", "")
                     for decl in model.get_internals_blocks()[0].get_declarations()}

        return model, metadata, internals

    def test_precompute_reciprocals(self):
        model, metadata, internals = self._transform()

        # reciprocals are inserted before the first propagator, in order of first use; identical denominators share a reciprocal
        assert list(internals.keys()) == ["__h", "__inv_tau", "__inv_tau_a", "__inv_tau_b", "__inv_expr0", "__P__x__x", "__P__x__y", "__P__y__y"]
        assert internals["__inv_tau"] == "1.0/(tau)"
        assert internals["__inv_expr0"] == "1.0/(C_m*(tau_a-tau_b))"

        assert internals["__P__x__x"] == "exp(-__h*__inv_tau)"
        assert internals["__P__x__y"] == "tau_a*tau_b*(exp(-__h*__inv_tau_a)-exp(-__h*__inv_tau_b))*__inv_expr0"
        assert internals["__P__y__y"] == "__inv_tau+x/__h+3*__inv_tau"    # division by a non-constant (``__h``) is left as it is

        assert set(metadata["test_model"]["precomputed_reciprocals"].keys()) == {"__inv_tau", "__inv_tau_a", "__inv_tau_b", "__inv_expr0"}

        # the symbol table should know about the new internals
        assert [sym.get_symbol_name() for sym in model.get_internal_symbols()] == list(internals.keys())

    def test_skip_exp_arguments(self):
        model, metadata, internals = self._transform({"skip_exp_arguments": True, "prefix": "__recip_"})

        assert internals["__P__x__x"] == "exp(-__h/tau)"
        assert internals["__P__x__y"] == "tau_a*tau_b*(exp(-__h/tau_a)-exp(-__h/tau_b))*__recip_expr0"
        assert internals["__P__y__y"] == "__recip_tau+x/__h+3*__recip_tau"
        assert set(metadata["test_model"]["precomputed_reciprocals"].keys()) == {"__recip_expr0", "__recip_tau"}


class TestNESTPrecomputeReciprocals:
    r"""Generate NEST code for neuron models with and without the ``precompute_reciprocals`` option, and check that the propagators in the generated code no longer contain divisions by parameters, and that the simulation results are the same (up to floating-point round-off)."""

    neuron_models = ["iaf_psc_exp_neuron", "iaf_psc_alpha_neuron"]

    # receptor types (and sign of the weight) for excitatory and inhibitory input
    receptor_types = {"iaf_psc_exp_neuron": {"exc": (0, 1.), "inh": (0, -1.)},
                      "iaf_psc_alpha_neuron": {"exc": (1, 1.), "inh": (2, 1.)}}

    suffixes = {False: "_nestml", True: "_nestml_recip"}

    @staticmethod
    def target_path(precompute: bool) -> str:
        return "test_precompute_reciprocals_target" + TestNESTPrecomputeReciprocals.suffixes[precompute]

    @staticmethod
    def module_name(precompute: bool) -> str:
        return "nestml_reciprocals_" + ("on" if precompute else "off") + "_module"

    @pytest.fixture(scope="class", autouse=True)
    def generate_code(self):
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "models", "neurons", neuron_model + ".nestml"))
                      for neuron_model in self.neuron_models]

        for precompute in [False, True]:
            generate_nest_target(input_path=input_path,
                                 target_path=self.target_path(precompute),
                                 logging_level="WARNING",
                                 module_name=self.module_name(precompute),
                                 suffix=self.suffixes[precompute],
                                 codegen_opts={"precompute_reciprocals": precompute})

    @pytest.mark.parametrize("neuron_model", neuron_models)
    def test_generated_code(self, neuron_model: str):
        check_generated_code(self.target_path(False), neuron_model + self.suffixes[False],
                             self.target_path(True), neuron_model + self.suffixes[True])

    def run_simulation(self, neuron_model: str, precompute: bool, sim_time: float = 1000.):
        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.SetKernelStatus({"resolution": .1,
                              "rng_seed": 42})

        try:
            nest.Install(self.module_name(precompute))
        except Exception:
            pass    # module already installed

        neuron = nest.Create(neuron_model + self.suffixes[precompute])
        exc_pg = nest.Create("poisson_generator", params={"rate": 8000.})
        inh_pg = nest.Create("poisson_generator", params={"rate": 2000.})
        mm = nest.Create("multimeter", params={"record_from": ["V_m"],
                                               "interval": .1})
        sr = nest.Create("spike_recorder")

        for pg, port, weight in [(exc_pg, "exc", 50.), (inh_pg, "inh", 50.)]:
            receptor_type, sign = self.receptor_types[neuron_model][port]
            nest.Connect(pg, neuron, syn_spec={"weight": sign * weight,
                                               "receptor_type": receptor_type})

        nest.Connect(mm, neuron)
        nest.Connect(neuron, sr)

        nest.Simulate(sim_time)

        return {"V_m": mm.get("events")["V_m"],
                "spike_times": sr.get("events")["times"]}

    @pytest.mark.parametrize("neuron_model", neuron_models)
    def test_simulation_results_identical(self, neuron_model: str):
        ref = self.run_simulation(neuron_model, precompute=False)
        res = self.run_simulation(neuron_model, precompute=True)

        # sanity check that the test is meaningful: the neuron fires
        assert len(ref["spike_times"]) > 10

        # x / tau and x * (1 / tau) differ in floating point by at most a few ULPs
        np.testing.assert_array_equal(ref["spike_times"], res["spike_times"])
        np.testing.assert_allclose(ref["V_m"], res["V_m"], rtol=1E-9, atol=1E-9)


class TestNESTPrecomputeReciprocalsNeuronSynapsePair:
    r"""Like :py:class:`TestNESTPrecomputeReciprocals`, but for a co-generated neuron and (STDP) synapse. The presynaptic trace stays in the synapse, where its propagator is evaluated at runtime for a variable timestep ``__h`` (the time since the last spike); the postsynaptic trace is moved into the neuron."""

    suffixes = {False: "_nestml_pair", True: "_nestml_pair_recip"}

    @staticmethod
    def neuron_model_name(precompute: bool) -> str:
        suffix = TestNESTPrecomputeReciprocalsNeuronSynapsePair.suffixes[precompute]
        return "iaf_psc_exp_neuron" + suffix + "__with_stdp_synapse" + suffix

    @staticmethod
    def synapse_model_name(precompute: bool) -> str:
        suffix = TestNESTPrecomputeReciprocalsNeuronSynapsePair.suffixes[precompute]
        return "stdp_synapse" + suffix + "__with_iaf_psc_exp_neuron" + suffix

    @staticmethod
    def target_path(precompute: bool) -> str:
        return "test_precompute_reciprocals_target" + TestNESTPrecomputeReciprocalsNeuronSynapsePair.suffixes[precompute]

    @staticmethod
    def module_name(precompute: bool) -> str:
        return "nestml_reciprocals_pair_" + ("on" if precompute else "off") + "_module"

    @pytest.fixture(scope="class", autouse=True)
    def generate_code(self):
        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("models", "synapses", "stdp_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, fn)) for fn in files]

        for precompute in [False, True]:
            codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                      "synapses": {"stdp_synapse": {"post_ports": ["post_spikes"]}}}],
                            "weight_variable": {"stdp_synapse": "w"},
                            "precompute_reciprocals": precompute}

            if not NESTTools.detect_nest_version().startswith("v2"):
                codegen_opts["neuron_parent_class"] = "StructuralPlasticityNode"
                codegen_opts["neuron_parent_class_include"] = "structural_plasticity_node.h"

            generate_nest_target(input_path=input_path,
                                 target_path=self.target_path(precompute),
                                 logging_level="WARNING",
                                 module_name=self.module_name(precompute),
                                 suffix=self.suffixes[precompute],
                                 codegen_opts=codegen_opts)

    @pytest.mark.parametrize("model", ["neuron", "synapse"])
    def test_generated_code(self, model: str):
        model_name = self.neuron_model_name if model == "neuron" else self.synapse_model_name
        check_generated_code(self.target_path(False), model_name(False),
                             self.target_path(True), model_name(True))

    def run_simulation(self, precompute: bool, sim_time: float = 1000.):
        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.SetKernelStatus({"resolution": .1,
                              "rng_seed": 42})

        try:
            nest.Install(self.module_name(precompute))
        except Exception:
            pass    # module already installed

        pre_pg = nest.Create("poisson_generator", params={"rate": 20.})
        pre_neurons = nest.Create("parrot_neuron", 10)
        post_pg = nest.Create("poisson_generator", params={"rate": 4000.})
        post_neuron = nest.Create(self.neuron_model_name(precompute))
        mm = nest.Create("multimeter", params={"record_from": ["V_m"],
                                               "interval": .1})
        sr = nest.Create("spike_recorder")

        nest.Connect(pre_pg, pre_neurons)
        nest.Connect(post_pg, post_neuron, syn_spec={"weight": 60.})
        nest.Connect(pre_neurons, post_neuron, syn_spec={"synapse_model": self.synapse_model_name(precompute),
                                                         "weight": 50.,
                                                         "delay": 1.})
        nest.Connect(mm, post_neuron)
        nest.Connect(post_neuron, sr)

        nest.Simulate(sim_time)

        syn = nest.GetConnections(source=pre_neurons, synapse_model=self.synapse_model_name(precompute))

        return {"V_m": mm.get("events")["V_m"],
                "spike_times": sr.get("events")["times"],
                "w": np.array(syn.get("w"))}

    def test_simulation_results_identical(self):
        ref = self.run_simulation(precompute=False)
        res = self.run_simulation(precompute=True)

        # sanity check that the test is meaningful: the postsynaptic neuron fires and the weights change
        assert len(ref["spike_times"]) > 10
        assert not np.allclose(ref["w"], 50.)

        # x / tau and x * (1 / tau) differ in floating point by at most a few ULPs
        np.testing.assert_array_equal(ref["spike_times"], res["spike_times"])
        np.testing.assert_allclose(ref["V_m"], res["V_m"], rtol=1E-9, atol=1E-9)
        np.testing.assert_allclose(ref["w"], res["w"], rtol=1E-9, atol=1E-9)

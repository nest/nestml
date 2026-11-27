# -*- coding: utf-8 -*-
#
# test_nest_t_spike_variable.py
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

import glob
import os

import pytest

from pynestml.cocos.co_co_nest_no_t_spike_variable import CoCoNESTNoTSpikeVariable
from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
from pynestml.exceptions.code_generation_exception import CodeGenerationException
from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import MessageCode
from pynestml.utils.model_parser import ModelParser


class TestNESTTSpikeVariable:
    r"""Tests that when generating code for NEST, no variable in a neuron model may be named ``t_spike``, as this name is reserved by NEST (``ArchivingNode`` uses it to report the time of the last emitted spike in the status dictionary). Synapse models are not restricted."""

    @pytest.mark.parametrize("block", [
        "    state:\n        t_spike ms = 0 ms\n",
        "    parameters:\n        t_spike ms = 2 ms\n",
        "    internals:\n        t_spike ms = 2 ms\n",
        "    update:\n        t_spike ms = 2 ms\n",
        "    equations:\n        inline t_spike ms = 2 ms\n"])
    def test_t_spike_variable_illegal(self, tmp_path, block):
        model_name = "t_spike_variable_illegal_neuron"
        input_path = os.path.join(tmp_path, model_name + ".nestml")
        with open(input_path, "w") as f:
            f.write("model " + model_name + ":\n" + block)

        with pytest.raises(CodeGenerationException):
            generate_nest_target(input_path,
                                 target_path=os.path.join(tmp_path, "target"),
                                 logging_level="DEBUG")

        assert len(Logger.get_messages(model_name, LoggingLevel.ERROR, message_code=MessageCode.NEST_T_SPIKE_VARIABLE)) == 1

    def test_t_spike_variable_legal_in_synapse(self, tmp_path):
        r"""Check that synapse models may contain a variable named ``t_spike``"""
        model_name = "t_spike_variable_legal_synapse"
        input_path = os.path.join(tmp_path, model_name + ".nestml")
        with open(input_path, "w") as f:
            f.write("model " + model_name + ":\n"
                    "    state:\n"
                    "        w real = 1\n"
                    "        t_spike ms = 0 ms\n"
                    "\n"
                    "    input:\n"
                    "        pre_spikes <- spike\n"
                    "\n"
                    "    output:\n"
                    "        spike\n"
                    "\n"
                    "    onReceive(pre_spikes):\n"
                    "        t_spike = t\n"
                    "        emit_spike(w)\n")

        self._init_predefined()
        ast_compilation_unit = ModelParser.parse_file(input_path)
        assert ast_compilation_unit is not None
        synapse = ast_compilation_unit.get_model_list()[0]
        assert not Logger.has_errors(synapse.name)

        NESTCodeGenerator().run_nest_target_specific_cocos(neurons=[], synapses=[synapse])    # raises CodeGenerationException in case of errors

        assert len(Logger.get_messages(None, LoggingLevel.ERROR, message_code=MessageCode.NEST_T_SPIKE_VARIABLE)) == 0

        # control: the same model would be flagged if it were checked as a neuron
        CoCoNESTNoTSpikeVariable.check_co_co(synapse)
        assert len(Logger.get_messages(None, LoggingLevel.ERROR, message_code=MessageCode.NEST_T_SPIKE_VARIABLE)) == 1

    def test_t_spike_variable_not_in_models_directory(self):
        r"""Check that none of the neuron models in the models directory trigger the coco"""
        models_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "models"))
        fnames = sorted(glob.glob(os.path.join(models_dir, "neurons", "*.nestml")))
        assert fnames

        self._init_predefined()

        for fname in fnames:
            ast_compilation_unit = ModelParser.parse_file(fname)
            assert ast_compilation_unit is not None, "Could not parse model in " + fname
            for model in ast_compilation_unit.get_model_list():
                CoCoNESTNoTSpikeVariable.check_co_co(model)

        assert len(Logger.get_messages(None, LoggingLevel.ERROR, message_code=MessageCode.NEST_T_SPIKE_VARIABLE)) == 0

    @staticmethod
    def _init_predefined():
        SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
        PredefinedUnits.register_units()
        PredefinedTypes.register_types()
        PredefinedVariables.register_variables()
        PredefinedFunctions.register_functions()
        Logger.init_logger(LoggingLevel.ERROR)

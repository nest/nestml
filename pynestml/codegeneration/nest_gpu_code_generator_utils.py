# -*- coding: utf-8 -*-
#
# nest_gpu_code_generator_utils.py
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

from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.symbols.variable_symbol import BlockType
from pynestml.meta_model.ast_variable import ASTVariable


class NESTGPUCodeGeneratorUtils:

    @classmethod
    def print_symbol_origin(cls, variable_symbol: VariableSymbol, variable: ASTVariable, is_synapse: bool = True) -> str:
        """
        Returns a prefix corresponding to the origin of the variable symbol.
        :param variable_symbol: a single variable symbol.
        :param variable: a single AST variable.
        :param is_synapse: whether the variable symbol belongs to a synapse or not.
        :return: the corresponding prefix
        """
        if variable_symbol.block_type in [BlockType.STATE, BlockType.EQUATION]:
            if not is_synapse:
                if "_is_numeric" in dir(variable) and variable._is_numeric:
                    return "y[%s]"
                return "var[%s]"
            else:
                return "ConnectionStateVars[base_idx + %s]"

        if variable_symbol.is_spike_input_port():
            return "var[N_SCAL_VAR + %s]"

        if variable_symbol.block_type in [BlockType.PARAMETERS, BlockType.INTERNALS] or variable_symbol.is_continuous_input_port():
            return "param[%s]"

        return ""

    @classmethod
    def replace_text_between_tags(cls, filepath, replace_str, begin_tag="// <<BEGIN_NESTML_GENERATED>>",
                                  end_tag="// <<END_NESTML_GENERATED>>", n=1):
        import re

        with open(filepath, "r") as f:
            file_str = f.read()

        begin_matches = list(re.finditer(re.escape(begin_tag), file_str))
        end_matches = list(re.finditer(re.escape(end_tag), file_str))

        try:
            start_pos = begin_matches[n - 1].end() if n > 0 else begin_matches[n].end()
            end_pos = end_matches[n - 1].start() if n > 0 else end_matches[n].start()
        except IndexError:
            raise ValueError(f"Could not find occurrence {n} of begin_tag/end_tag in {filepath}")

        file_str = file_str[:start_pos] + replace_str + file_str[end_pos:]
        with open(filepath, "w") as f:
            f.write(file_str)

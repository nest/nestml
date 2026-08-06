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
    def print_symbol_origin(cls, variable_symbol: VariableSymbol, variable: ASTVariable) -> str:
        """
        Returns a prefix corresponding to the origin of the variable symbol.
        :param variable_symbol: a single variable symbol.
        :return: the corresponding prefix
        """
        if variable_symbol.block_type in [BlockType.STATE, BlockType.EQUATION]:
            if "_is_numeric" in dir(variable) and variable._is_numeric:
                return "y[%s]"
            return "var[%s]"

        if variable_symbol.is_spike_input_port():
            return "var[N_SCAL_VAR + %s]"

        if variable_symbol.block_type in [BlockType.PARAMETERS, BlockType.INTERNALS] or variable_symbol.is_continuous_input_port():
            return "param[%s]"

        return ""

    @classmethod
    def replace_text_between_tags(cls, filepath, replace_str, begin_tag="// <<BEGIN_NESTML_GENERATED>>",
                                  end_tag="// <<END_NESTML_GENERATED>>", rfind=False):
        with open(filepath, "r") as f:
            file_str = f.read()

        # Find the start and end positions of the tags
        if rfind:
            start_pos = file_str.rfind(begin_tag) + len(begin_tag)
            end_pos = file_str.rfind(end_tag)
        else:
            start_pos = file_str.find(begin_tag) + len(begin_tag)
            end_pos = file_str.find(end_tag)

        # Concatenate the new string between the start and end tags and write it back to the file
        file_str = file_str[:start_pos] + replace_str + file_str[end_pos:]
        with open(filepath, "w") as f:
            f.write(file_str)
        f.close()

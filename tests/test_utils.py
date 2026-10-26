# -*- coding: utf-8 -*-
#
# test_utils.py
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

from typing import Optional

import numpy as np

from pynestml.meta_model.ast_model import ASTModel
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.model_parser import ModelParser


def get_trace_at(t, t_spikes, tau, initial=0., increment=1., before_increment=False, extra_debug=False):
    r"""Compute the value at any given time ``t`` of a synaptic trace value that gets incremented by ``increment`` upon each spike in ``t_spikes`` and exponentially decays back to zero with time constant ``tau``."""
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


def parse_and_validate_model(fname: str) -> Optional[str]:
    from pynestml.frontend.pynestml_frontend import generate_target

    SymbolTable.initialize_symbol_table(
        ASTSourceLocation(
            start_line=0,
            start_column=0,
            end_line=0,
            end_column=0))
    PredefinedUnits.register_units()
    PredefinedTypes.register_types()
    PredefinedVariables.register_variables()
    PredefinedFunctions.register_functions()

    Logger.init_logger(LoggingLevel.DEBUG)

    generate_target(input_path=fname, target_platform="NONE", logging_level="DEBUG")

    ast_compilation_unit = ModelParser.parse_file(fname)
    if ast_compilation_unit is None or len(ast_compilation_unit.get_model_list()) == 0:
        return None

    model: ASTModel = ast_compilation_unit.get_model_list()[0]
    model_name = model.get_name()

    return model_name

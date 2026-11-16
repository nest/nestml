# -*- coding: utf-8 -*-
#
# type_caster.py
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

from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class TypeCaster:
    r"""
    Checks whether the type of an expression can be used where a different type is expected.

    Physical types are compared by their dimension only (for instance, ``mV`` and ``V`` are the same type), so no magnitude conversion is ever necessary here.
    """

    @staticmethod
    def try_to_recover_or_error(_lhs_type_symbol, _rhs_type_symbol, _containing_expression):
        if _rhs_type_symbol.is_castable_to(_lhs_type_symbol):
            code, message = Messages.get_implicit_cast_rhs_to_lhs(_rhs_type_symbol.print_symbol(),
                                                                  _lhs_type_symbol.print_symbol())
            Logger.log_message(error_position=_containing_expression.get_source_position(),
                               code=code, message=message, log_level=LoggingLevel.INFO)
            return

        code, message = Messages.get_type_different_from_expected(_lhs_type_symbol, _rhs_type_symbol)
        Logger.log_message(error_position=_containing_expression.get_source_position(),
                           code=code, message=message, log_level=LoggingLevel.ERROR)

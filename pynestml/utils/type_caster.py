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

from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.logging_helper import LoggingHelper
from pynestml.utils.messages import Messages


class TypeCaster(object):
    @staticmethod
    def do_magnitude_conversion_rhs_to_lhs(_rhs_type_symbol, _lhs_type_symbol, _containing_expression):
        """
        determine conversion factor from rhs to lhs, register it with the relevant expression, drop warning
        """
        _containing_expression.set_implicit_conversion_factor(
            UnitTypeSymbol.get_conversion_factor(_lhs_type_symbol.astropy_unit,
                                                 _rhs_type_symbol.astropy_unit))
        _containing_expression.type = _lhs_type_symbol

        code, message = Messages.get_implicit_magnitude_conversion(_lhs_type_symbol, _rhs_type_symbol,
                                                                   _containing_expression.get_implicit_conversion_factor())
        Logger.log_message(code=code, message=message,
                           error_position=_containing_expression.get_source_position(),
                           log_level=LoggingLevel.WARNING)

    @staticmethod
    def try_to_recover_or_error(_lhs_type_symbol, _rhs_type_symbol, _containing_expression):
        if _rhs_type_symbol.is_castable_to(_lhs_type_symbol):
            if isinstance(_lhs_type_symbol, UnitTypeSymbol) \
                    and isinstance(_rhs_type_symbol, UnitTypeSymbol):
                conversion_factor = UnitTypeSymbol.get_conversion_factor(
                    _lhs_type_symbol.astropy_unit,  _rhs_type_symbol.astropy_unit)
                if not conversion_factor == 1.:
                    # the units are mutually convertible, but require a factor unequal to 1 (e.g. mV and A*Ohm)
                    TypeCaster.do_magnitude_conversion_rhs_to_lhs(
                        _rhs_type_symbol, _lhs_type_symbol, _containing_expression)
            # the units are mutually convertible (e.g. V and A*Ohm)
            code, message = Messages.get_implicit_cast_rhs_to_lhs(_rhs_type_symbol.print_symbol(),
                                                                  _lhs_type_symbol.print_symbol())
            Logger.log_message(error_position=_containing_expression.get_source_position(),
                               code=code, message=message, log_level=LoggingLevel.INFO)
        else:
            code, message = Messages.get_type_different_from_expected(_lhs_type_symbol, _rhs_type_symbol)
            Logger.log_message(error_position=_containing_expression.get_source_position(),
                               code=code, message=message, log_level=LoggingLevel.ERROR)

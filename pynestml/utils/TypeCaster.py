#
# UnitCaster.py
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

from pynestml.symbols.UnitTypeSymbol import UnitTypeSymbol
from pynestml.utils.Logger import Logger, LoggingLevel
from pynestml.utils.LoggingHelper import LoggingHelper
from pynestml.utils.Messages import Messages


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
        if _rhs_type_symbol.differs_only_in_magnitude_or_is_equal_to(_lhs_type_symbol):
            TypeCaster.do_magnitude_conversion_rhs_to_lhs(_rhs_type_symbol, _lhs_type_symbol, _containing_expression)
        elif _rhs_type_symbol.is_castable_to(_lhs_type_symbol):
            LoggingHelper.drop_implicit_cast_warning(_containing_expression.get_source_position(), _lhs_type_symbol,
                                                     _rhs_type_symbol)
        else:
            LoggingHelper.drop_incompatible_types_error(_containing_expression, _lhs_type_symbol, _rhs_type_symbol)

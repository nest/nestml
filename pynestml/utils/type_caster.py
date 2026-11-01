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

from typing import Optional

from pynestml.codegeneration.nest_unit_converter import NESTUnitConverter
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.implicit_conversion_factor import ImplicitConversionFactor
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class TypeCaster:
    @staticmethod
    def get_implicit_conversion_factor(_rhs_type_symbol, _lhs_type_symbol, _containing_expression, is_compound_product_or_quotient: bool = False) -> Optional[ImplicitConversionFactor]:
        """
        Determine conversion factor from rhs to lhs (see ImplicitConversionFactor), or None if the units cannot be converted

        :param is_compound_product_or_quotient: True if ``_containing_expression`` is the right-hand side of a compound product or quotient, such as ``V_m *= 2 V/mV``. Then ``_rhs_type_symbol`` is the type of the converted value, for instance ``mV*V/mV``, and the factor applies to ``_containing_expression``.
        """
        factor = UnitTypeSymbol.get_conversion_factor(_rhs_type_symbol.astropy_unit, _lhs_type_symbol.astropy_unit)
        if factor is None:
            return None

        if is_compound_product_or_quotient:
            # generated code must multiply or divide the variable by the value of the expression without a unit, that is, by the value in a unit with scale 1, whatever the unit in which generated code holds the variable
            return ImplicitConversionFactor.from_held_unit_scales(factor, ASTUtils.get_held_unit_scale(_containing_expression), 1.)

        rhs_scale = None
        if _rhs_type_symbol.equals(_containing_expression.type):
            # the converted value is the value of the expression
            rhs_scale = ASTUtils.get_held_unit_scale(_containing_expression)

        return ImplicitConversionFactor.from_held_unit_scales(factor, rhs_scale, NESTUnitConverter.get_held_unit_scale(_lhs_type_symbol.astropy_unit))

    @staticmethod
    def do_magnitude_conversion_rhs_to_lhs(_rhs_type_symbol, _lhs_type_symbol, _containing_expression, conversion_factor: Optional[ImplicitConversionFactor] = None):
        """
        Determine conversion factor from rhs to lhs, register it with the relevant expression

        :param conversion_factor: the factor, if it was already computed with get_implicit_conversion_factor()
        """
        if conversion_factor is None:
            conversion_factor = TypeCaster.get_implicit_conversion_factor(_rhs_type_symbol, _lhs_type_symbol, _containing_expression)

        _containing_expression.set_implicit_conversion_factor(conversion_factor)
        code, message = Messages.get_implicit_magnitude_conversion(_lhs_type_symbol, _rhs_type_symbol,
                                                                   _containing_expression.get_implicit_conversion_factor())
        Logger.log_message(code=code, message=message,
                           error_position=_containing_expression.get_source_position(),
                           log_level=LoggingLevel.INFO)

    @staticmethod
    def try_to_recover_or_error(_lhs_type_symbol, _rhs_type_symbol, _containing_expression, set_implicit_conversion_factor_on_lhs=False, is_compound_product_or_quotient: bool = False):
        if _rhs_type_symbol.is_castable_to(_lhs_type_symbol):
            if isinstance(_lhs_type_symbol, UnitTypeSymbol) \
                    and isinstance(_rhs_type_symbol, UnitTypeSymbol):
                conversion_factor = TypeCaster.get_implicit_conversion_factor(_rhs_type_symbol, _lhs_type_symbol, _containing_expression, is_compound_product_or_quotient)

                if conversion_factor is None:
                    # error during conversion
                    code, message = Messages.get_type_different_from_expected(_lhs_type_symbol, _rhs_type_symbol)
                    Logger.log_message(error_position=_containing_expression.get_source_position(),
                                       code=code, message=message, log_level=LoggingLevel.ERROR)
                    return

                if set_implicit_conversion_factor_on_lhs and not (conversion_factor == 1. and conversion_factor.nest_factor == 1.):
                    # the units are mutually convertible, but require a factor unequal to 1 (e.g. mV and A*Ohm), possibly only in generated code (e.g. Hz and s**-1)
                    TypeCaster.do_magnitude_conversion_rhs_to_lhs(_rhs_type_symbol, _lhs_type_symbol, _containing_expression, conversion_factor)

            # the units are mutually convertible (e.g. V and A*Ohm)
            code, message = Messages.get_implicit_cast_rhs_to_lhs(_rhs_type_symbol.print_symbol(),
                                                                  _lhs_type_symbol.print_symbol())
            Logger.log_message(error_position=_containing_expression.get_source_position(),
                               code=code, message=message, log_level=LoggingLevel.INFO)
            return

        code, message = Messages.get_type_different_from_expected(_lhs_type_symbol, _rhs_type_symbol)
        Logger.log_message(error_position=_containing_expression.get_source_position(),
                           code=code, message=message, log_level=LoggingLevel.ERROR)

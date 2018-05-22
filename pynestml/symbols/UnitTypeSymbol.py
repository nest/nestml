#
# UnitTypeSymbol.py
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

from pynestml.symbols.TypeSymbol import TypeSymbol
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class UnitTypeSymbol(TypeSymbol):
    unit = None

    @property
    def astropy_unit(self):
        return self.unit.get_unit()

    def is_numeric(self):
        return True

    def is_primitive(self):
        return False

    def __init__(self, _unit):
        self.unit = _unit
        super(UnitTypeSymbol, self).__init__(name=str(_unit.get_unit()))

    def print_nestml_type(self):
        return self.unit.print_unit()

    def print_nest_type(self):
        return 'double'

    def equals(self, other=None):
        basic_equals = super(UnitTypeSymbol, self).equals(other)
        # defer comparison of units to sympy library
        if basic_equals is True:
            self_unit = self.astropy_unit
            other_unit = other.astropy_unit
            # TODO: astropy complains this is deprecated
            return self_unit == other_unit

        return False

    def __mul__(self, other):
        from pynestml.symbols.ErrorTypeSymbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        if other.is_instance_of(UnitTypeSymbol):
            return self.multiply_by(other)
        if other.is_numeric_primitive():
            return self
        return self.binary_operation_not_defined_error('*', other)

    def multiply_by(self, other):
        from pynestml.symbols.PredefinedTypes import PredefinedTypes
        return PredefinedTypes.get_type(self.astropy_unit * other.astropy_unit)

    def __truediv__(self, other):
        from pynestml.symbols.ErrorTypeSymbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        if other.is_instance_of(UnitTypeSymbol):
            return self.divide_by(other)
        if other.is_numeric_primitive():
            return self
        return self.binary_operation_not_defined_error('/', other)

    def __div__(self, other):
        return self.__truediv__(other)

    def divide_by(self, other):
        from pynestml.symbols.PredefinedTypes import PredefinedTypes
        return PredefinedTypes.get_type(self.astropy_unit / other.astropy_unit)

    def __neg__(self):
        return self

    def __pos__(self):
        return self

    def __invert__(self):
        return self.unary_operation_not_defined_error('~')

    def __pow__(self, power, modulo=None):
        from pynestml.symbols.ErrorTypeSymbol import ErrorTypeSymbol
        if isinstance(power, ErrorTypeSymbol):
            return power
        if isinstance(power, int):
            return self.to_the_power_of(power)
        return self.binary_operation_not_defined_error('**', power)

    def to_the_power_of(self, power):
        from pynestml.symbols.PredefinedTypes import PredefinedTypes
        return PredefinedTypes.get_type(self.astropy_unit ** power)

    def __add__(self, other):
        from pynestml.symbols.ErrorTypeSymbol import ErrorTypeSymbol
        from pynestml.symbols.StringTypeSymbol import StringTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        if other.is_instance_of(StringTypeSymbol):
            return other
        if other.is_numeric_primitive():
            return self.warn_implicit_cast_from_to(other, self)
        if other.is_instance_of(UnitTypeSymbol):
            return self.add_or_sub_another_unit(other)
        return self.binary_operation_not_defined_error('+', other)

    def __sub__(self, other):
        from pynestml.symbols.ErrorTypeSymbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        if other.is_numeric_primitive():
            return self.warn_implicit_cast_from_to(other, self)
        if other.is_instance_of(UnitTypeSymbol):
            return self.add_or_sub_another_unit(other)
        return self.binary_operation_not_defined_error('-', other)

    def add_or_sub_another_unit(self, other):
        if self.equals(other):
            return other
        else:
            return self.attempt_magnitude_cast(other)

    def attempt_magnitude_cast(self, _other):
        if self.differs_only_in_magnitude_or_is_equal_to(_other):
            factor = UnitTypeSymbol.get_conversion_factor(self.astropy_unit, _other.astropy_unit)
            _other.referenced_object.set_implicit_conversion_factor(factor)
            code, message = Messages.get_implicit_magnitude_conversion(self, _other, factor)
            Logger.log_message(code=code, message=message,
                               error_position=self.referenced_object.get_source_position(),
                               log_level=LoggingLevel.WARNING)
            return self
        else:
            return self.binary_operation_not_defined_error('+/-', _other)

    # TODO: change order of parameters to conform with the from_to scheme.
    # TODO: Also rename to reflect that, i.e. get_conversion_factor_from_to
    @classmethod
    def get_conversion_factor(cls, to, _from):
        """
        Calculates the conversion factor from _convertee_unit to target_unit.
        Behaviour is only well-defined if both units have the same physical base type
        """
        factor = (_from / to).si.scale
        return factor

    def is_castable_to(self, _other_type):
        from pynestml.symbols.RealTypeSymbol import RealTypeSymbol
        if _other_type.is_instance_of(RealTypeSymbol):
            return True
        else:
            return False

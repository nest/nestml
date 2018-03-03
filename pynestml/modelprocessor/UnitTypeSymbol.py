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
from copy import copy

from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.TypeSymbol import TypeSymbol
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class UnitTypeSymbol(TypeSymbol):
    unit = None

    @property
    def astropy_unit(self):
        return self.unit.getUnit()

    def isNumeric(self):
        return True

    def isPrimitive(self):
        return False

    def __init__(self, _unit):
        self.unit = _unit
        super(UnitTypeSymbol,self).__init__(_name=str(_unit.getUnit()))

    def print_symbol(self):
        result = self.unit.printUnit()
        if self.is_buffer:
            result += ' buffer'
        return result

    def _get_concrete_nest_type(self):
        return 'double'

    def equals(self, _other=None):
        basic_equals = super(UnitTypeSymbol,self).equals(_other)
        # defer comparison of units to sympy library
        if basic_equals is True:
            self_unit = self.astropy_unit
            other_unit = _other.astropy_unit
            # TODO: astropy complains this is deprecated
            return self_unit == other_unit

        return False

    def __mul__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return copy(other)
        if other.is_instance_of(UnitTypeSymbol):
            return self.multiply_by(other)
        if other.isNumericPrimitive():
            return copy(self)
        return self.binary_operation_not_defined_error('*', other)

    def multiply_by(self, other):
        return PredefinedTypes.getTypeIfExists(self.astropy_unit * other.astropy_unit)

    def __truediv__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return copy(other)
        if other.is_instance_of(UnitTypeSymbol):
            return self.divide_by(other)
        if other.isNumericPrimitive():
            return copy(self)
        return self.binary_operation_not_defined_error('*', other)

    def divide_by(self, other):
        return PredefinedTypes.getTypeIfExists(self.astropy_unit / other.astropy_unit)

    def __neg__(self):
        return copy(self)

    def __pos__(self):
        return copy(self)

    def __invert__(self):
        return self.unary_operation_not_defined_error('~')

    def __pow__(self, power, modulo=None):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        if isinstance(power, ErrorTypeSymbol):
            return copy(power)
        if isinstance(power, int):
            return self.to_the_power_of(power)
        return self.binary_operation_not_defined_error('**', power)

    def to_the_power_of(self, power):
        return PredefinedTypes.getTypeIfExists(self.astropy_unit ** power)

    def __add__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        from pynestml.modelprocessor.StringTypeSymbol import StringTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return copy(other)
        if other.is_instance_of(StringTypeSymbol):
            return copy(other)
        if other.isNumericPrimitive():
            return self.warn_implicit_cast_from_to(other, self)
        if other.is_instance_of(UnitTypeSymbol):
            return self.add_or_sub_another_unit(other)
        return self.binary_operation_not_defined_error('+', other)

    def __sub__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return copy(other)
        if other.isNumericPrimitive():
            return self.warn_implicit_cast_from_to(other, self)
        if other.is_instance_of(UnitTypeSymbol):
            return self.add_or_sub_another_unit(other)
        return self.binary_operation_not_defined_error('-', other)

    def add_or_sub_another_unit(self, other):
        if self.equals(other):
            return copy(other)
        else:
            return self.attempt_magnitude_cast(other)

    def attempt_magnitude_cast(self, _other):
        if self.differs_only_in_magnitude_or_is_equal_to(_other):
            factor = UnitTypeSymbol.get_conversion_factor(self.astropy_unit, _other.astropy_unit)
            _other.referenced_object.setImplicitConversionFactor(factor)
            code, message = Messages.get_implicit_magnitude_conversion(self, _other, factor)
            Logger.logMessage(_code=code, _message=message,
                              _errorPosition=self.referenced_object.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.WARNING)
            return copy(self)
        else:
            return self.binary_operation_not_defined_error('+/-', _other)

    # TODO: change order of parameters to conform with the from_to scheme.
    # TODO: Also rename to reflect that, i.e. get_conversion_factor_from_to
    @classmethod
    def get_conversion_factor(cls, _to, _from):
        """
        Calculates the conversion factor from _convertee_unit to _targe_unit.
        Behaviour is only well-defined if both units have the same physical base type
        """
        factor = (_from / _to).si.scale
        return factor

    def is_castable_to(self, _other_type):
        from pynestml.modelprocessor.RealTypeSymbol import RealTypeSymbol
        if _other_type.is_instance_of(RealTypeSymbol):
            return True
        else:
            return False

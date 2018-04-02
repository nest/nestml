#
# ASTDataTypeVisitor.py
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


class ASTDataTypeVisitor(object):
    """
    This class represents a visitor which inspects a handed over data type, checks if correct typing has been used
    (e.g., no computation between primitive and non primitive data types etc.) and finally updates the type symbols
    of the datatype ast.
    """

    @classmethod
    def visitDatatype(cls, _dataType=None):
        """
        Visits a single data type ast node and updates, checks correctness and updates its type symbol.
        This visitor can also be used to derive the original name of the unit.
        :param _dataType: a single datatype node.
        :type _dataType: ASTDataType
        """
        from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
        from pynestml.modelprocessor.ASTDataType import ASTDataType
        assert (_dataType is not None and isinstance(_dataType, ASTDataType)), \
            '(PyNestML.SymbolTable.DatatypeVisitor) No or wrong type of data-type provided (%s)!' % type(_dataType)
        if _dataType.is_unit_type():
            symbol = cls.visitUnitType(_dataType.get_unit_type())
            _dataType.set_type_symbol(symbol)
        elif _dataType.is_integer():
            symbol = PredefinedTypes.getIntegerType()
            _dataType.set_type_symbol(symbol)
        elif _dataType.is_real():
            symbol = PredefinedTypes.getRealType()
            _dataType.set_type_symbol(symbol)
        elif _dataType.is_string():
            symbol = PredefinedTypes.getStringType()
            _dataType.set_type_symbol(symbol)
        elif _dataType.is_boolean():
            symbol = PredefinedTypes.getBooleanType()
            _dataType.set_type_symbol(symbol)
        elif _dataType.is_void():
            symbol = PredefinedTypes.getVoidType()
            _dataType.set_type_symbol(symbol)
        else:
            symbol = None
        if symbol is not None:
            return symbol.get_symbol_name()
        else:
            return 'UNKNOWN'  # this case can actually never happen

    @classmethod
    def visitUnitType(cls, _unitType=None):
        """
        Visits a single unit type element, checks for correct usage of units and builds the corresponding combined 
        unit.
        :param _unitType: a single unit type ast.
        :type _unitType: ASTUnitType
        :return: a new type symbol representing this unit type.
        :rtype: TypeSymbol
        """
        from pynestml.modelprocessor.ASTUnitType import ASTUnitType
        from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
        assert (_unitType is not None and isinstance(_unitType, ASTUnitType)), \
            '(PyNestML.SymbolTable.DatatypeVisitor) No or wrong type of unit-typ provided (%s)!' % type(_unitType)
        if _unitType.is_pow:
            base_symbol = cls.visitUnitType(_unitType.base)
            exponent = _unitType.exponent
            sympy_unit = base_symbol.get_encapsulated_unit() ** exponent
            return cls.__handleUnit(sympy_unit)
        elif _unitType.is_encapsulated:
            return cls.visitUnitType(_unitType.compound_unit)
        elif _unitType.is_div:
            if isinstance(_unitType.get_lhs(), ASTUnitType):  # regard that lhs can be a numeric or a unit-type
                lhs = cls.visitUnitType(_unitType.get_lhs()).get_encapsulated_unit()
            else:
                lhs = _unitType.get_lhs()
            rhs = cls.visitUnitType(_unitType.get_rhs()).get_encapsulated_unit()
            res = lhs / rhs
            return cls.__handleUnit(res)
        elif _unitType.is_times:
            if isinstance(_unitType.get_lhs(), ASTUnitType):  # regard that lhs can be a numeric or a unit-type
                lhs = cls.visitUnitType(_unitType.get_lhs()).get_encapsulated_unit()
            else:
                lhs = _unitType.get_lhs()
            rhs = cls.visitUnitType(_unitType.get_rhs()).get_encapsulated_unit()
            res = lhs * rhs
            return cls.__handleUnit(res)
        elif _unitType.is_simple_unit():
            type_s = PredefinedTypes.getTypeIfExists(_unitType.unit)
            if type_s is None:
                raise UnknownAtomicUnit('Unknown atomic unit %s.' % _unitType.unit)
            else:
                return type_s
        return

    @classmethod
    def __handleUnit(cls, _unitType=None):
        """
        Handles a handed over unit by creating the corresponding unit-type, storing it in the list of predefined
        units, creating a type symbol and returning it.
        :param _unitType: a single sympy unit symbol
        :type _unitType: Symbol (sympy)
        :return: a new type symbol
        :rtype: TypeSymbol
        """
        from astropy import units
        from pynestml.modelprocessor.UnitType import UnitType
        from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
        from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
        from pynestml.modelprocessor.TypeSymbol import TypeSymbol
        # first ensure that it does not already exists, if not create it and register it in the set of predefined units
        assert (_unitType is not None), \
            '(PyNestML.Visitor.UnitTypeVisitor) No unit-type provided (%s)!' % type(_unitType)
        # first clean up the unit of not required components, here it is the 1.0 in front of the unit
        # e.g., 1.0 * 1 / ms. This step is not mandatory for correctness, but makes  reporting easier
        if isinstance(_unitType, units.Quantity) and _unitType.value == 1.0:
            to_process = _unitType.unit
        else:
            to_process = _unitType
        if str(to_process) not in PredefinedUnits.getUnits().keys():
            unit_type = UnitType(_name=str(to_process), _unit=to_process)
            PredefinedUnits.registerUnit(unit_type)
        # now create the corresponding type symbol if it does not exists
        if PredefinedTypes.getTypeIfExists(str(to_process)) is None:
            type_symbol = TypeSymbol(name=str(to_process),
                                     unit=PredefinedUnits.getUnitIfExists(str(to_process)),
                                     is_integer=False, is_real=False, is_void=False,
                                     is_boolean=False, is_string=False, is_buffer=False)
            PredefinedTypes.registerType(type_symbol)
        return PredefinedTypes.getTypeIfExists(_name=str(to_process))


class UnknownAtomicUnit(Exception):
    """
    This exception is thrown whenever a not known atomic unit is used, e.g., pacoV.
    """
    pass

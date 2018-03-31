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
        if _dataType.isUnitType():
            symbol = cls.visitUnitType(_dataType.getUnitType())
            _dataType.setTypeSymbol(symbol)
        elif _dataType.isInteger():
            symbol = PredefinedTypes.getIntegerType()
            _dataType.setTypeSymbol(symbol)
        elif _dataType.isReal():
            symbol = PredefinedTypes.getRealType()
            _dataType.setTypeSymbol(symbol)
        elif _dataType.isString():
            symbol = PredefinedTypes.getStringType()
            _dataType.setTypeSymbol(symbol)
        elif _dataType.isBoolean():
            symbol = PredefinedTypes.getBooleanType()
            _dataType.setTypeSymbol(symbol)
        elif _dataType.isVoid():
            symbol = PredefinedTypes.getVoidType()
            _dataType.setTypeSymbol(symbol)
        else:
            symbol = None
        if symbol is not None:
            return symbol.getSymbolName()
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
        if _unitType.isPowerExpression():
            base_symbol = cls.visitUnitType(_unitType.getBase())
            exponent = _unitType.getExponent()
            sympy_unit = base_symbol.getEncapsulatedUnit() ** exponent
            return cls.__handleUnit(sympy_unit)
        elif _unitType.isEncapsulated():
            return cls.visitUnitType(_unitType.getCompoundUnit())
        elif _unitType.isDiv():
            if isinstance(_unitType.getLhs(), ASTUnitType):  # regard that lhs can be a numeric or a unit-type
                lhs = cls.visitUnitType(_unitType.getLhs()).getEncapsulatedUnit()
            else:
                lhs = _unitType.getLhs()
            rhs = cls.visitUnitType(_unitType.getRhs()).getEncapsulatedUnit()
            res = lhs / rhs
            return cls.__handleUnit(res)
        elif _unitType.isTimes():
            if isinstance(_unitType.getLhs(), ASTUnitType):  # regard that lhs can be a numeric or a unit-type
                lhs = cls.visitUnitType(_unitType.getLhs()).getEncapsulatedUnit()
            else:
                lhs = _unitType.getLhs()
            rhs = cls.visitUnitType(_unitType.getRhs()).getEncapsulatedUnit()
            res = lhs * rhs
            return cls.__handleUnit(res)
        elif _unitType.isSimpleUnit():
            type_s = PredefinedTypes.getTypeIfExists(_unitType.getSimpleUnit())
            if type_s is None:
                raise UnknownAtomicUnit('Unknown atomic unit %s.' % _unitType.getSimpleUnit())
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
            type_symbol = TypeSymbol(_name=str(to_process),
                                     _unit=PredefinedUnits.getUnitIfExists(str(to_process)),
                                     _isInteger=False, _isReal=False, _isVoid=False,
                                     _isBoolean=False, _isString=False, _isBuffer=False)
            PredefinedTypes.registerType(type_symbol)
        return PredefinedTypes.getTypeIfExists(_name=str(to_process))


class UnknownAtomicUnit(Exception):
    """
    This exception is thrown whenever a not known atomic unit is used, e.g., pacoV.
    """
    pass

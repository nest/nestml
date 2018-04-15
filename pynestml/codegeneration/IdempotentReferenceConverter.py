#
# IdempotentReferenceConverter.py
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
from pynestml.codegeneration.IReferenceConverter import IReferenceConverter
from pynestml.utils.ASTUtils import ASTUtils


class IdempotentReferenceConverter(IReferenceConverter):
    """
    Returns the same input as output, i.e., an identity mapping of elements is preformed. This converter is used
    whenever comments have to be printed, in order to preserve the initial PyNestML syntax.
    """

    def convertUnaryOp(self, _unaryOperator):
        """
        Returns the same string.
        :param _unaryOperator: a single unary operator string.
        :type _unaryOperator: ASTUnaryOperator
        :return: the same string
        :rtype: str
        """
        return str(_unaryOperator) + '%s'

    def convertNameReference(self, _astVariable):
        """
        Returns the same string
        :param _astVariable: a single variable
        :type _astVariable: ASTVariable
        :return: the same string
        :rtype: str
        """
        from pynestml.ast.ASTVariable import ASTVariable
        assert (_astVariable is not None and isinstance(_astVariable, ASTVariable)), \
            '(PyNestML.CodeGeneration.ReferenceConverter) No or wrong type of variable provided (%s)!' % type(
                _astVariable)
        return _astVariable.get_complete_name()

    def convertFunctionCall(self, _astFunctionCall):
        """
        Returns the same function call back.
        :param _astFunctionCall: a function call
        :type _astFunctionCall: ASTFunctionCall
        :return: the same sting back
        :rtype: str
        """
        from pynestml.ast.ASTFunctionCall import ASTFunctionCall
        assert (_astFunctionCall is not None and isinstance(_astFunctionCall, ASTFunctionCall)), \
            '(PyNestML.CodeGeneration.ReferenceConverter) No or wrong type of function call provided (%s)!' % type(
                _astFunctionCall)

        result = _astFunctionCall.get_name()
        if ASTUtils.needs_arguments(_astFunctionCall):
            result += '(%s)'
        else:
            result += '()'
        return result

    def convertBinaryOp(self, _binaryOperator):
        """
        Returns the same binary operator back.
        :param _binaryOperator:  a single binary operator
        :type _binaryOperator: str
        :return: the same binary operator
        :rtype: str
        """
        return '%s' + str(_binaryOperator) + '%s'

    def convertConstant(self, _constantName):
        """
        Returns the same string back.
        :param _constantName: a constant name
        :type _constantName: str
        :return: the same string
        :rtype: str
        """
        return _constantName

    def convertTernaryOperator(self):
        """
        Converts the ternary operator to its initial shape.
        :return: a string representation
        :rtype: str
        """
        return '(' + '%s' + ')?(' + '%s' + '):(' + '%s' + ')'

    def convertLogicalOperator(self, _op):
        return str(_op)

    def convertArithmeticOperator(self, _op):
        return str(_op)

    def convertEncapsulated(self):
        return '(%s)'

    def convertComparisonOperator(self, _op):
        return str(_op)

    def convertLogicalNot(self):
        return 'not'

    def convertBitOperator(self, _op):
        return str(_op)

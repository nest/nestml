#
# NESTReferenceConverter.py
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
from pynestml.ast.ASTFunctionCall import ASTFunctionCall
from pynestml.ast.ASTVariable import ASTVariable
from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.codegeneration.IReferenceConverter import IReferenceConverter
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.codegeneration.UnitConverter import UnitConverter
from pynestml.symbols.PredefinedFunctions import PredefinedFunctions
from pynestml.symbols.PredefinedUnits import PredefinedUnits
from pynestml.symbols.PredefinedVariables import PredefinedVariables
from pynestml.symbols.Symbol import SymbolKind
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Logger import Logger, LoggingLevel
from pynestml.utils.Messages import Messages


class NESTReferenceConverter(IReferenceConverter):
    """
    This concrete reference converter is used to transfer internal names to counter-pieces in NEST.
    """

    __usesGSL = False

    def __init__(self, _usesGSL=False):
        """
        Standard constructor.
        :param _usesGSL: indicates whether GSL is used.
        :type _usesGSL: bool
        """
        assert (_usesGSL is not None and isinstance(_usesGSL, bool)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of uses-gsl provided (%s)!' % type(
                _usesGSL)
        self.__usesGSL = _usesGSL
        return

    @classmethod
    def convertBinaryOp(cls, _binaryOperator):
        """
        Converts a single binary operator to nest processable format.
        :param _binaryOperator: a single binary operator string.
        :type _binaryOperator: AST_
        :return: the corresponding nest representation
        :rtype: str
        """
        from pynestml.ast.ASTArithmeticOperator import ASTArithmeticOperator
        from pynestml.ast.ASTBitOperator import ASTBitOperator
        from pynestml.ast.ASTComparisonOperator import ASTComparisonOperator
        from pynestml.ast.ASTLogicalOperator import ASTLogicalOperator
        if isinstance(_binaryOperator, ASTArithmeticOperator):
            return cls.convertArithmeticOperator(_binaryOperator)
        if isinstance(_binaryOperator, ASTBitOperator):
            return cls.convertBitOperator(_binaryOperator)
        if isinstance(_binaryOperator, ASTComparisonOperator):
            return cls.convertComparisonOperator(_binaryOperator)
        if isinstance(_binaryOperator, ASTLogicalOperator):
            return cls.convertLogicalOperator(_binaryOperator)
        else:
            Logger.log_message('Cannot determine binary operator!', LoggingLevel.ERROR)
            return '(%s) ERROR (%s)'

    @classmethod
    def convertFunctionCall(cls, _astFunctionCall):
        """
        Converts a single handed over function call to nest processable format.
        :param _astFunctionCall: a single function call
        :type _astFunctionCall:  ASTFunctionCall
        :return: a string representation
        :rtype: str
        """
        assert (_astFunctionCall is not None and isinstance(_astFunctionCall, ASTFunctionCall)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of uses-gsl provided (%s)!' % type(
                _astFunctionCall)
        function_name = _astFunctionCall.get_name()
        if function_name == 'and':
            return '&&'
        elif function_name == 'or':
            return '||'
        elif function_name == 'resolution':
            return 'nest::Time::get_resolution().get_ms()'
        elif function_name == 'steps':
            return 'nest::Time(nest::Time::ms((double) %s)).get_steps()'
        elif function_name == PredefinedFunctions.POW:
            return 'std::pow(%s)'
        elif function_name == PredefinedFunctions.MAX or function_name == PredefinedFunctions.BOUNDED_MAX:
            return 'std::max(%s)'
        elif function_name == PredefinedFunctions.MIN or function_name == PredefinedFunctions.BOUNDED_MIN:
            return 'std::min(%s)'
        elif function_name == PredefinedFunctions.EXP:
            return 'std::exp(%s)'
        elif function_name == PredefinedFunctions.LOG:
            return 'std::log(%s)'
        elif function_name == 'expm1':
            return 'numerics::expm1(%s)'
        elif function_name == PredefinedFunctions.EMIT_SPIKE:
            return 'set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n' \
                   'nest::SpikeEvent se;\n' \
                   'nest::kernel().event_delivery_manager.send(*this, se, lag)'
        elif ASTUtils.needs_arguments(_astFunctionCall):
            return function_name + '(%s)'
        else:
            return function_name + '()'

    def convertNameReference(self, _astVariable):
        """
        Converts a single variable to nest processable format.
        :param _astVariable: a single variable.
        :type _astVariable: ASTVariable
        :return: a nest processable format.
        :rtype: str
        """
        from pynestml.codegeneration.NestPrinter import NestPrinter
        assert (_astVariable is not None and isinstance(_astVariable, ASTVariable)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of uses-gsl provided (%s)!' % type(
                _astVariable)
        variable_name = NestNamesConverter.convertToCPPName(_astVariable.get_complete_name())

        if PredefinedUnits.is_unit(_astVariable.get_complete_name()):
            return str(
                UnitConverter.getFactor(PredefinedUnits.get_unit(_astVariable.get_complete_name()).get_unit()))
        if variable_name == PredefinedVariables.E_CONSTANT:
            return 'numerics::e'
        else:
            symbol = _astVariable.get_scope().resolve_to_symbol(variable_name, SymbolKind.VARIABLE)
            if symbol is None:
                # this should actually not happen, but an error message is better than an exception
                code, message = Messages.getCouldNotResolve(variable_name)
                Logger.log_message(log_level=LoggingLevel.ERROR, code=code, message=message,
                                   error_position=_astVariable.get_source_position())
                return ''
            else:
                if symbol.is_local():
                    return variable_name + ('[i]' if symbol.has_vector_parameter() else '')
                elif symbol.is_buffer():
                    return NestPrinter.printOrigin(symbol) + NestNamesConverter.bufferValue(symbol) \
                           + ('[i]' if symbol.has_vector_parameter() else '')
                else:
                    if symbol.is_function():
                        return 'get_' + variable_name + '()' + ('[i]' if symbol.has_vector_parameter() else '')
                    else:
                        if symbol.is_init_values():
                            return NestPrinter.printOrigin(symbol) + \
                                   (GSLNamesConverter.name(symbol)
                                   if self.__usesGSL else NestNamesConverter.name(symbol)) + \
                                   ('[i]' if symbol.has_vector_parameter() else '')
                        else:
                            return NestPrinter.printOrigin(symbol) + \
                                   NestNamesConverter.name(symbol) + \
                                   ('[i]' if symbol.has_vector_parameter() else '')

    @classmethod
    def convertConstant(cls, _constantName):
        """
        Converts a single handed over constant.
        :param _constantName: a constant as string.
        :type _constantName: str
        :return: the corresponding nest representation
        :rtype: str
        """
        if _constantName == 'inf':
            return 'std::numeric_limits<double_t>::infinity()'
        else:
            return _constantName

    @classmethod
    def convertUnaryOp(cls, _unaryOperator):
        """
        Depending on the concretely used operator, a string is returned.
        :param _unaryOperator: a single operator.
        :type _unaryOperator:  str
        :return: the same operator
        :rtype: str
        """
        from pynestml.ast.ASTUnaryOperator import ASTUnaryOperator
        assert (_unaryOperator is not None and isinstance(_unaryOperator, ASTUnaryOperator)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of unary operator provided (%s)!' \
            % type(_unaryOperator)
        if _unaryOperator.isUnaryPlus():
            return '(' + '+' + '%s' + ')'
        elif _unaryOperator.isUnaryMinus():
            return '(' + '-' + '%s' + ')'
        elif _unaryOperator.isUnaryTilde():
            return '(' + '~' + '%s' + ')'
        else:
            Logger.log_message('Cannot determine unary operator!', LoggingLevel.ERROR)
            return '(' + '%s' + ')'

    @classmethod
    def convertEncapsulated(cls):
        """
        Converts the encapsulating parenthesis to NEST style.
        :return: a set of parenthesis
        :rtype: str
        """
        return '(%s)'

    @classmethod
    def convertLogicalNot(cls):
        """
        Returns a representation of the logical not in NEST.
        :return: a string representation
        :rtype: str
        """
        return '(' + '!' + '%s' + ')'

    @classmethod
    def convertLogicalOperator(cls, _op):
        """
        Prints a logical operator in NEST syntax.
        :param _op: a logical operator object
        :type _op: ASTLogicalOperator
        :return: a string representation
        :rtype: str
        """
        from pynestml.ast.ASTLogicalOperator import ASTLogicalOperator
        assert (_op is not None and isinstance(_op, ASTLogicalOperator)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of logical operator provided (%s)!' \
            % type(_op)
        if _op.is_and():
            return '%s' + '&&' + '%s'
        elif _op.is_or():
            return '%s' + '||' + '%s'
        else:
            Logger.log_message('Cannot determine logical operator!', LoggingLevel.ERROR)
            return '(%s) ERROR  (%s)'

    @classmethod
    def convertComparisonOperator(cls, _op):
        """
        Prints a logical operator in NEST syntax.
        :param _op: a logical operator object
        :type _op: ASTLogicalOperator
        :return: a string representation
        :rtype: str
        """
        from pynestml.ast.ASTComparisonOperator import ASTComparisonOperator
        assert (_op is not None and isinstance(_op, ASTComparisonOperator)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of logical operator provided (%s)!' \
            % type(_op)
        if _op.isLt():
            return '%s' + '<' + '%s'
        elif _op.isLe():
            return '%s' + '<=' + '%s'
        elif _op.isEq():
            return '%s' + '==' + '%s'
        elif _op.isNe() or _op.isNe2():
            return '%s' + '!=' + '%s'
        elif _op.isGe():
            return '%s' + '>=' + '%s'
        elif _op.isGt():
            return '%s' + '>' + '%s'
        else:
            Logger.log_message('Cannot determine comparison operator!', LoggingLevel.ERROR)
            return '(%s) ERROR  (%s)'

    @classmethod
    def convertBitOperator(cls, _op):
        """
        Prints a logical operator in NEST syntax.
        :param _op: a logical operator object
        :type _op: ASTLogicalOperator
        :return: a string representation
        :rtype: str
        """
        from pynestml.ast.ASTBitOperator import ASTBitOperator
        assert (_op is not None and isinstance(_op, ASTBitOperator)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of bit operator provided (%s)!' \
            % type(_op)
        if _op.isBitShiftLeft():
            return '%s' + '<<' '%s'
        if _op.isBitShiftRight():
            return '%s' + '>>' + '%s'
        if _op.isBitAnd():
            return '%s' + '&' + '%s'
        if _op.isBitOr():
            return '%s' + '|' + '%s'
        if _op.isBitXor():
            return '%s' + '^' + '%s'
        else:
            Logger.log_message('Cannot determine bit operator!', LoggingLevel.ERROR)
            return '(%s) ERROR (%s)'

    @classmethod
    def convertArithmeticOperator(cls, _op):
        """
        Prints a logical operator in NEST syntax.
        :param _op: a logical operator object
        :type _op: ASTLogicalOperator
        :return: a string representation
        :rtype: str
        """
        from pynestml.ast.ASTArithmeticOperator import ASTArithmeticOperator
        assert (_op is not None and isinstance(_op, ASTArithmeticOperator)), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of arithmetic operator provided (%s)!' \
            % type(_op)
        if _op.is_plus_op:
            return '%s' + '+' + '%s'
        if _op.is_minus_op:
            return '%s' + '-' + '%s'
        if _op.is_times_op:
            return '%s' + '*' + '%s'
        if _op.is_div_op:
            return '%s' + '/' + '%s'
        if _op.is_modulo_op:
            return '%s' + '%' + '%s'
        if _op.is_pow_op:
            return 'pow' + '(%s,%s)'
        else:
            Logger.log_message('Cannot determine arithmetic operator!', LoggingLevel.ERROR)
            return '(%s) ERROR (%s)'

    @classmethod
    def convertTernaryOperator(cls):
        """
        Prints a ternary operator in NEST syntax.
        :return: a string representation
        :rtype: str
        """
        return '(' + '%s' + ')?(' + '%s' + '):(' + '%s' + ')'

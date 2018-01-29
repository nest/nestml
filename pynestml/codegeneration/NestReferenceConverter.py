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
from pynestml.codegeneration.IReferenceConverter import IReferenceConverter
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.codegeneration.UnitConverter import UnitConverter
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages
from pynestml.utils.ASTUtils import ASTUtils


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
        from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
        from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
        from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
        from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
        if isinstance(_binaryOperator, ASTArithmeticOperator):
            return cls.convertArithmeticOperator(_binaryOperator)
        if isinstance(_binaryOperator, ASTBitOperator):
            return cls.convertBitOperator(_binaryOperator)
        if isinstance(_binaryOperator, ASTComparisonOperator):
            return cls.convertComparisonOperator(_binaryOperator)
        if isinstance(_binaryOperator, ASTLogicalOperator):
            return cls.convertLogicalOperator(_binaryOperator)
        else:
            Logger.logMessage('Cannot determine binary operator!', LOGGING_LEVEL.ERROR)
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
        functionName = _astFunctionCall.getName()
        if functionName == 'and':
            return '&&'
        elif functionName == 'or':
            return '||'
        elif functionName == 'resolution':
            return 'nest::Time::get_resolution().get_ms()'
        elif functionName == 'steps':
            return 'nest::Time(nest::Time::ms((double) %s)).get_steps()'
        elif functionName == PredefinedFunctions.POW:
            return 'std::pow(%s)'
        elif functionName == PredefinedFunctions.MAX or functionName == PredefinedFunctions.BOUNDED_MAX:
            return 'std::max(%s)'
        elif functionName == PredefinedFunctions.MIN or functionName == PredefinedFunctions.BOUNDED_MIN:
            return 'std::min(%s)'
        elif functionName == PredefinedFunctions.EXP:
            return 'std::exp(%s)'
        elif functionName == PredefinedFunctions.LOG:
            return 'std::log(%s)'
        elif functionName == 'expm1':
            return 'numerics::expm1(%s)'
        elif functionName == PredefinedFunctions.EMIT_SPIKE:
            return 'set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n' \
                   'nest::SpikeEvent se;\n' \
                   'nest::kernel().event_delivery_manager.send(*this, se, lag)'
        elif ASTUtils.needsArguments(_astFunctionCall):
            return functionName + '(%s)'
        else:
            return functionName + '()'

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
        variableName = NestNamesConverter.convertToCPPName(_astVariable.getCompleteName())

        if PredefinedUnits.isUnit(_astVariable.getCompleteName()):
            return str(
                UnitConverter.getFactor(PredefinedUnits.getUnitIfExists(_astVariable.getCompleteName()).getUnit()))
        if variableName == PredefinedVariables.E_CONSTANT:
            return 'numerics::e'
        else:
            symbol = _astVariable.getScope().resolveToSymbol(variableName, SymbolKind.VARIABLE)
            if symbol is None:
                # this should actually not happen, but an error message is better than an exception
                code, message = Messages.getCouldNotResolve(variableName)
                Logger.logMessage(_logLevel=LOGGING_LEVEL.ERROR, _code=code, _message=message,
                                  _errorPosition=_astVariable.getSourcePosition())
                return ''
            else:
                if symbol.isLocal():
                    return variableName + ('[i]' if symbol.hasVectorParameter() else '')
                elif symbol.isBuffer():
                    return NestPrinter.printOrigin(symbol) + NestNamesConverter.bufferValue(symbol) \
                           + ('[i]' if symbol.hasVectorParameter() else '')
                else:
                    if symbol.isFunction():
                        return 'get_' + variableName + '()' + ('[i]' if symbol.hasVectorParameter() else '')
                    else:
                        if symbol.isInitValues():
                            return NestPrinter.printOrigin(symbol) + \
                                   (GSLNamesConverter.name(symbol)
                                    if self.__usesGSL else NestNamesConverter.name(symbol)) + \
                                   ('[i]' if symbol.hasVectorParameter() else '')
                        else:
                            return NestPrinter.printOrigin(symbol) + \
                                   NestNamesConverter.name(symbol) + \
                                   ('[i]' if symbol.hasVectorParameter() else '')

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
        from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
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
            Logger.logMessage('Cannot determine unary operator!', LOGGING_LEVEL.ERROR)
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
        from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
        assert (_op is not None and isinstance(_op, ASTLogicalOperator)), \
            '(PyNestML.CodeGeneration.NestReferenceConverter) No or wrong type of logical operator provided (%s)!' \
            % type(_op)
        if _op.isAnd():
            return '%s' + '&&' + '%s'
        elif _op.isOr():
            return '%s' + '||' + '%s'
        else:
            Logger.logMessage('Cannot determine logical operator!', LOGGING_LEVEL.ERROR)
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
        from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
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
            Logger.logMessage('Cannot determine comparison operator!', LOGGING_LEVEL.ERROR)
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
        from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
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
            Logger.logMessage('Cannot determine bit operator!', LOGGING_LEVEL.ERROR)
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
        from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
        assert (_op is not None and isinstance(_op, ASTArithmeticOperator)), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of arithmetic operator provided (%s)!' \
            % type(_op)
        if _op.isPlusOp():
            return '%s' + '+' + '%s'
        if _op.isMinusOp():
            return '%s' + '-' + '%s'
        if _op.isTimesOp():
            return '%s' + '*' + '%s'
        if _op.isDivOp():
            return '%s' + '/' + '%s'
        if _op.isModuloOp():
            return '%s' + '%' + '%s'
        if _op.isPowOp():
            return 'pow' + '(%s,%s)'
        else:
            Logger.logMessage('Cannot determine arithmetic operator!', LOGGING_LEVEL.ERROR)
            return '(%s) ERROR (%s)'

    @classmethod
    def convertTernaryOperator(cls):
        """
        Prints a ternary operator in NEST syntax.
        :return: a string representation
        :rtype: str
        """
        return '(' + '%s' + ')?(' + '%s' + '):(' + '%s' + ')'

#
# PredefinedFunctions.py
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
from pynestml.nestml.PredefinedTypes import PredefinedTypes
from pynestml.nestml.FunctionSymbol import FunctionSymbol


class PredefinedFunctions:
    """
    This class is used to represent all predefined functions of NESTML.
    
    Attributes:
        __TIME_RESOLUTION       The callee name of the resolution function.
        __TIME_STEPS            The callee name of the time-steps function.
        __EMIT_SPIKE            The callee name of the emit-spike function.
        __PRINT                 The callee name of the print function.
        __PRINTLN               The callee name of the println function.
        __POW                   The callee name of the power function.
        __EXP                   The callee name of the exponent function.
        __LOG                   The callee name of the logarithm function.
        __LOGGER_INFO           The callee name of the logger-info function.
        __LOGGER_WARNING        The callee name of the logger-warning function.
        __RANDOM                The callee name of the random function.
        __RANDOM_INT            The callee name of the random int function.
        __EXPM1                 The callee name of the exponent (alternative) function.
        __DELTA                 The callee name of the delta function.
        __MAX                   The callee name of the max function.
        __BOUNDED_MAX           The callee name of the bounded-max function.
        __MIN                   The callee name of the min function.
        __BOUNDED_MIN           The callee name of the bounded-min function.     
        __INTEGRATE_ODES        The callee name of the integrate-ode function.
        __CURR_SUM              The callee name of the curr-sum function.
        __COND_SUM              The callee name of the cond-sum function.
        __CONVOLVE              The callee name of the convolve function. 
        __name2FunctionSymbol   A dict of function symbols as currently defined.
    """
    TIME_RESOLUTION = 'resolution'
    TIME_STEPS = 'steps'
    EMIT_SPIKE = 'emit_spike'
    PRINT = 'print'
    PRINTLN = 'println'
    POW = 'pow'
    EXP = 'exp'
    LOG = 'log'
    LOGGER_INFO = 'info'
    LOGGER_WARNING = 'warning'
    RANDOM = 'random'
    RANDOM_INT = 'randomInt'
    EXPM1 = 'expm1'
    DELTA = 'delta'
    MAX = 'max'
    BOUNDED_MAX = 'bounded_max'
    MIN = 'min'
    BOUNDED_MIN = 'bounded_min'
    INTEGRATE_ODES = 'integrate_odes'
    CURR_SUM = 'curr_sum'
    COND_SUM = 'cond_sum'
    CONVOLVE = 'convolve'
    __name2FunctionSymbol = {}  # a map dict from function-names to symbols

    @classmethod
    def registerPredefinedFunctions(cls):
        """
        Registers all predefined functions.
        """
        cls.__name2FunctionSymbol = {}
        cls.__registerTimeResolutionFunction()
        cls.__registerTimeStepsFunction()
        cls.__registerEmitSpikeFunction()
        cls.__registerPrintFunction()
        cls.__registerPrintLnFunction()
        cls.__registerPowerFunction()
        cls.__registerExponentFunction()
        cls.__registerLogFunction()
        cls.__registerLoggerInfoFunction()
        cls.__registerLoggerWarningFunction()
        cls.__registerRandomFunction()
        cls.__registerRandomIntFunction()
        cls.__registerExp1Function()
        cls.__registerDeltaFunction()
        cls.__registerMaxFunction()
        cls.__registerMaxBoundedFunction()
        cls.__registerMinFunction()
        cls.__registerMinBoundedFunction()
        cls.__registerIntegratedOdesFunction()
        cls.__registerCurrSumFunction()
        cls.__registerCondSumFunction()
        cls.__registerConvolve()
        return

    @classmethod
    def __registerTimeStepsFunction(cls):
        """
        Registers the time-resolution.
        """
        params = list()
        params.append(PredefinedTypes.getTypeIfExists('ms'))
        symbol = FunctionSymbol(_name=cls.TIME_STEPS, _paramTypes=params,
                                _returnType=PredefinedTypes.getIntegerType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.TIME_STEPS] = symbol
        return

    @classmethod
    def __registerEmitSpikeFunction(cls):
        """
        Registers the emit-spike function.
        """
        symbol = FunctionSymbol(_name=cls.EMIT_SPIKE, _paramTypes=list(),
                                _returnType=PredefinedTypes.getRealType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.EMIT_SPIKE] = symbol
        return

    @classmethod
    def __registerPrintFunction(cls):
        """
        Registers the print function.
        """
        params = list()
        params.append(PredefinedTypes.getStringType())
        symbol = FunctionSymbol(_name=cls.PRINT, _paramTypes=params,
                                _returnType=PredefinedTypes.getVoidType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.PRINT] = symbol
        return

    @classmethod
    def __registerPrintLnFunction(cls):
        """
        Registers the print-line function.
        """
        symbol = FunctionSymbol(_name=cls.PRINTLN, _paramTypes=list(),
                                _returnType=PredefinedTypes.getVoidType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.PRINTLN] = symbol
        return

    @classmethod
    def __registerPowerFunction(cls):
        """
        Registers the power function.
        """
        params = list()
        params.append(PredefinedTypes.getRealType())  # the base type
        params.append(PredefinedTypes.getRealType())  # the exponent type
        symbol = FunctionSymbol(_name=cls.POW, _paramTypes=params,
                                _returnType=PredefinedTypes.getRealType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.POW] = symbol
        return

    @classmethod
    def __registerExponentFunction(cls):
        """
        Registers the exponent (e(X)) function.
        """
        params = list()
        params.append(PredefinedTypes.getRealType())  # the argument
        symbol = FunctionSymbol(_name=cls.EXP, _paramTypes=params,
                                _returnType=PredefinedTypes.getRealType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.EXP] = symbol
        return

    @classmethod
    def __registerLogFunction(cls):
        """
        Registers the logarithm function (to base 10).
        """
        params = list()
        params.append(PredefinedTypes.getRealType())  # the argument
        symbol = FunctionSymbol(_name=cls.LOG, _paramTypes=params,
                                _returnType=PredefinedTypes.getRealType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.LOG] = symbol
        return

    @classmethod
    def __registerLoggerInfoFunction(cls):
        """
        Registers the logger info method into the scope.
        """
        params = list()
        params.append(PredefinedTypes.getStringType())  # the argument
        symbol = FunctionSymbol(_name=cls.LOGGER_INFO, _paramTypes=params,
                                _returnType=PredefinedTypes.getVoidType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.LOGGER_INFO] = symbol
        return

    @classmethod
    def __registerLoggerWarningFunction(cls):
        """
        Registers the logger warning method.
        """
        params = list()
        params.append(PredefinedTypes.getStringType())  # the argument
        symbol = FunctionSymbol(_name=cls.LOGGER_WARNING, _paramTypes=params,
                                _returnType=PredefinedTypes.getVoidType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.LOGGER_WARNING] = symbol
        return

    @classmethod
    def __registerRandomFunction(cls):
        """
        Registers the random method as used to generate a random real-typed value.
        """
        symbol = FunctionSymbol(_name=cls.RANDOM, _paramTypes=list(),
                                _returnType=PredefinedTypes.getRealType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.RANDOM] = symbol
        return

    @classmethod
    def __registerRandomIntFunction(cls):
        """
        Registers the random method as used to generate a random integer-typed value.
        """
        symbol = FunctionSymbol(_name=cls.RANDOM_INT, _paramTypes=list(),
                                _returnType=PredefinedTypes.getIntegerType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.RANDOM_INT] = symbol
        return

    @classmethod
    def __registerTimeResolutionFunction(cls):
        """
        Registers the time resolution function.
        """
        symbol = FunctionSymbol(_name=cls.TIME_RESOLUTION, _paramTypes=list(),
                                _returnType=PredefinedTypes.getTypeIfExists('ms'),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.TIME_RESOLUTION] = symbol
        return

    @classmethod
    def __registerExp1Function(cls):
        """
        Registers the alternative version of the exponent function, exp1.
        """
        params = list()
        params.append(PredefinedTypes.getRealType())  # the argument
        symbol = FunctionSymbol(_name=cls.EXPM1, _paramTypes=params,
                                _returnType=PredefinedTypes.getRealType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.EXPM1] = symbol
        return

    @classmethod
    def __registerDeltaFunction(cls):
        """
        Registers the delta function.
        """
        params = list()
        params.append(PredefinedTypes.getTypeIfExists('ms'))
        params.append(PredefinedTypes.getTypeIfExists('ms'))
        symbol = FunctionSymbol(_name=cls.DELTA, _paramTypes=params,
                                _returnType=PredefinedTypes.getRealType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.DELTA] = symbol
        return

    @classmethod
    def __registerMaxFunction(cls):
        """
        Registers the maximum function.
        """
        params = list()
        params.append(PredefinedTypes.getRealType())
        params.append(PredefinedTypes.getRealType())
        symbol = FunctionSymbol(_name=cls.MAX, _paramTypes=params,
                                _returnType=PredefinedTypes.getRealType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.MAX] = symbol
        return

    @classmethod
    def __registerMaxBoundedFunction(cls):
        """
        Registers the maximum (bounded) function.
        """
        params = list()
        params.append(PredefinedTypes.getRealType())
        params.append(PredefinedTypes.getRealType())
        symbol = FunctionSymbol(_name=cls.BOUNDED_MAX, _paramTypes=params,
                                _returnType=PredefinedTypes.getRealType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.BOUNDED_MAX] = symbol
        return

    @classmethod
    def __registerMinFunction(cls):
        """
        Registers the minimum function.
        """
        params = list()
        params.append(PredefinedTypes.getRealType())
        params.append(PredefinedTypes.getRealType())
        symbol = FunctionSymbol(_name=cls.MIN, _paramTypes=params,
                                _returnType=PredefinedTypes.getRealType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.MIN] = symbol
        return

    @classmethod
    def __registerMinBoundedFunction(cls):
        """
        Registers the minimum (bounded) function.
        """
        params = list()
        params.append(PredefinedTypes.getRealType())
        params.append(PredefinedTypes.getRealType())
        symbol = FunctionSymbol(_name=cls.BOUNDED_MIN, _paramTypes=params,
                                _returnType=PredefinedTypes.getRealType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.BOUNDED_MIN] = symbol
        return

    @classmethod
    def __registerIntegratedOdesFunction(cls):
        """
        Registers the integrate-odes function.
        """
        params = list()
        symbol = FunctionSymbol(_name=cls.INTEGRATE_ODES, _paramTypes=params,
                                _returnType=PredefinedTypes.getVoidType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.INTEGRATE_ODES] = symbol
        return

    @classmethod
    def __registerCurrSumFunction(cls):
        """
        Registers the curr_sum function into scope.
        """
        params = list()
        params.append(PredefinedTypes.getTypeIfExists('pA'))
        params.append(PredefinedTypes.getRealType())
        symbol = FunctionSymbol(_name=cls.CURR_SUM, _paramTypes=params,
                                _returnType=PredefinedTypes.getTypeIfExists('pA'),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.CURR_SUM] = symbol
        return

    @classmethod
    def __registerCondSumFunction(cls):
        """
        Registers the cond_sum function into scope.
        """
        params = list()
        params.append(PredefinedTypes.getTypeIfExists('nS'))
        params.append(PredefinedTypes.getRealType())
        symbol = FunctionSymbol(_name=cls.COND_SUM, _paramTypes=params,
                                _returnType=PredefinedTypes.getTypeIfExists('nS'),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.COND_SUM] = symbol
        return

    @classmethod
    def __registerConvolve(cls):
        """
        Registers the convolve function into the system.
        """
        params = list()
        params.append(PredefinedTypes.getRealType())
        params.append(PredefinedTypes.getRealType())
        symbol = FunctionSymbol(_name=cls.CONVOLVE, _paramTypes=params,
                                _returnType=PredefinedTypes.getRealType(),
                                _elementReference=None, _isPredefined=True)
        cls.__name2FunctionSymbol[cls.CONVOLVE] = symbol
        return

    @classmethod
    def getFunctionSymbols(cls):
        """
        Returns a copy of the dict containing all predefined functions symbols.
        :return: a copy of the dict containing the functions symbols
        :rtype: copy(dict(FunctionSymbol)
        """
        return cls.__name2FunctionSymbol

    @classmethod
    def getMethodSymbolIfExists(cls, _name=None):
        """
        Returns a copy of a element in the set of defined functions if one exists, otherwise None
        :param _name: the name of the function symbol
        :type _name: str
        :return: a copy of the element if such exists in the dict, otherwise None
        :rtype: None or FunctionSymbol
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.PredefinedFunctions) No or wrong type of name provided (%s)!' % type(_name)
        if _name in cls.__name2FunctionSymbol.keys():
            return cls.__name2FunctionSymbol[_name]
        else:
            return None

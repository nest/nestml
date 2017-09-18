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



class PredefinedFunctions:
    """
    This class is used to represent all predefined functions of NESTML.
    """
    __TIME_RESOLUTION = 'resolution'
    __TIME_STEPS = 'steps'
    __EMIT_SPIKE = 'emit_spike'
    __PRINT = 'print'
    __PRINTLN = 'println'
    __POW = 'pow'
    __EXP = 'exp'
    __LOG = 'log'
    __LOGGER_INFO = 'info'
    __LOGGER_WARNING = 'warning'
    __RANDOM = 'random'
    __RANDOM_INT = 'randomInt'
    __EXPM1 = 'expm1'
    __DELTA = 'delta'
    __MAX = 'max'
    __BOUNDED_MAX = 'bounded_max'
    __MIN = 'min'
    __BOUNDED_MIN = 'bounded_min'
    __INTEGRATE_ODES = 'integrate_odes'
    __CURR_SUM = 'curr_sum'
    __COND_SUM = 'cond_sum'

    @classmethod
    def registerPredefinedVariables(cls, _scope):
        """
        Registers all predefined functions into the handed over scope.
        :param _scope: a single scope.
        :type _scope: Scope
        """
        from pynestml.src.main.python.org.nestml.symbol_table.Scope import Scope
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.PredefinedFunctions) No or wrong type of scope handed over!'
        cls.__registerTimeStepsFunction(_scope)
        cls.__registerEmitSpikeFunction(_scope)
        cls.__registerPrintFunction(_scope)
        return

    @classmethod
    def __registerTimeStepsFunction(cls, _scope=None):
        """
        Registers the time-resolution into th scope.
        :param _scope: a single scope element.
        :type _scope: Scope
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        print('PredefinedFunctions.TODO: Time steps input real typed instead of ms!')
        params = list()
        params.append(TypeSymbol.getRealType())
        symbol = FunctionSymbol(_name=cls.__TIME_STEPS, _paramTypes=params,
                                _returnType=TypeSymbol.getIntegerType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerEmitSpikeFunction(cls, _scope=None):
        """
        Registers the emit function into th scope.
        :param _scope: a single scope element.
        :type _scope: Scope
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        symbol = FunctionSymbol(_name=cls.__EMIT_SPIKE, _paramTypes=list(),
                                _returnType=TypeSymbol.getRealType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerPrintFunction(cls, _scope=None):
        """
        Registers the print function into th scope.
        :param _scope: a single scope element.
        :type _scope: Scope
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        params = list()
        params.append(TypeSymbol.getStringType())
        symbol = FunctionSymbol(_name=cls.__PRINT, _paramTypes=params,
                                _returnType=TypeSymbol.getVoidType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerPrintLnFunction(cls, _scope=None):
        """
        Registers the print-line function into th scope.
        :param _scope: a single scope element.
        :type _scope: Scope
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        symbol = FunctionSymbol(_name=cls.__PRINTLN, _paramTypes=list(),
                                _returnType=TypeSymbol.getVoidType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerPowerFunction(cls, _scope):
        """
        Registers the power function into the scope.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        params = list()
        params.append(TypeSymbol.getRealType())  # the base type
        params.append(TypeSymbol.getRealType())  # the exponent type
        symbol = FunctionSymbol(_name=cls.__POW, _paramTypes=params,
                                _returnType=TypeSymbol.getRealType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerExponentFunction(cls, _scope):
        """
        Registers the exponent (e(X)) function into the scope.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        params = list()
        params.append(TypeSymbol.getRealType())  # the argument
        symbol = FunctionSymbol(_name=cls.__EXP, _paramTypes=params,
                                _returnType=TypeSymbol.getRealType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerLogFunction(cls, _scope):
        """
        Registers the logarithm function (to base 10) into the scope.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        params = list()
        params.append(TypeSymbol.getRealType())  # the argument
        symbol = FunctionSymbol(_name=cls.__LOG, _paramTypes=params,
                                _returnType=TypeSymbol.getRealType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerLoggerInfoFunction(cls, _scope):
        """
        Registers the logger info method into the scope.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        params = list()
        params.append(TypeSymbol.getStringType())  # the argument
        symbol = FunctionSymbol(_name=cls.__LOGGER_INFO, _paramTypes=params,
                                _returnType=TypeSymbol.getVoidType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerLoggerWarningFunction(cls, _scope):
        """
        Registers the logger warning method into the scope.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        params = list()
        params.append(TypeSymbol.getStringType())  # the argument
        symbol = FunctionSymbol(_name=cls.__LOGGER_WARNING, _paramTypes=params,
                                _returnType=TypeSymbol.getVoidType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerRandomFunction(cls, _scope):
        """
        Registers the random method into the scope as used to generate a random real-typed value.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        symbol = FunctionSymbol(_name=cls.__RANDOM, _paramTypes=list(),
                                _returnType=TypeSymbol.getRealType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerRandomIntFunction(cls, _scope):
        """
        Registers the random method into the scope as used to generate a random integer-typed value.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        symbol = FunctionSymbol(_name=cls.__RANDOM_INT, _paramTypes=list(),
                                _returnType=TypeSymbol.getIntegerType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerTimeResolutionFunction(cls, _scope):
        """
        Registers the time resolution function into the scope.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        print('PredefinedFunctions.TODO: Time resolution real typed instead of ms!')
        symbol = FunctionSymbol(_name=cls.__TIME_RESOLUTION, _paramTypes=list(),
                                _returnType=TypeSymbol.getRealType(),  # TODO here
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerExp1Function(cls, _scope):
        """
        Registers the alternative version of the exponent function, exp1.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        params = list()
        params.append(TypeSymbol.getRealType())  # the argument
        symbol = FunctionSymbol(_name=cls.__EXPM1, _paramTypes=params,
                                _returnType=TypeSymbol.getRealType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerDeltaFunction(cls, _scope):
        """
        Registers the delta function into scope.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        print('PredefinedFunctions.TODO: Delta function real typed instead of ms!')
        params = list()
        params.append(TypeSymbol.getRealType())  # todo here
        params.append(TypeSymbol.getRealType())  # todo here
        symbol = FunctionSymbol(_name=cls.__DELTA, _paramTypes=params,
                                _returnType=TypeSymbol.getRealType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerMaxFunction(cls, _scope):
        """
        Registers the maximum function into scope.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        params = list()
        params.append(TypeSymbol.getRealType())
        params.append(TypeSymbol.getRealType())
        symbol = FunctionSymbol(_name=cls.__MAX, _paramTypes=params,
                                _returnType=TypeSymbol.getRealType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerMaxBoundedFunction(cls, _scope):
        """
        Registers the maximum (bounded) function into scope.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        params = list()
        params.append(TypeSymbol.getRealType())
        params.append(TypeSymbol.getRealType())
        symbol = FunctionSymbol(_name=cls.__BOUNDED_MAX, _paramTypes=params,
                                _returnType=TypeSymbol.getRealType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerMinFunction(cls, _scope):
        """
        Registers the minimum function into scope.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        params = list()
        params.append(TypeSymbol.getRealType())
        params.append(TypeSymbol.getRealType())
        symbol = FunctionSymbol(_name=cls.__MIN, _paramTypes=params,
                                _returnType=TypeSymbol.getRealType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerMinBoundedFunction(cls, _scope):
        """
        Registers the minimum (bounded) function into scope.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        params = list()
        params.append(TypeSymbol.getRealType())
        params.append(TypeSymbol.getRealType())
        symbol = FunctionSymbol(_name=cls.__BOUNDED_MIN, _paramTypes=params,
                                _returnType=TypeSymbol.getRealType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerIntegratedOdesFunction(cls, _scope):
        """
        Registers the integrate-odes function into scope.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        params = list()
        symbol = FunctionSymbol(_name=cls.__INTEGRATE_ODES, _paramTypes=params,
                                _returnType=TypeSymbol.getVoidType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    @classmethod
    def __registerIntegratedOdesFunction(cls, _scope):
        """
        Registers the integrate-odes function into scope.
        :param _scope: a single scope element.
        :type _scope: Scope 
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.FunctionSymbol import FunctionSymbol
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        params = list()
        symbol = FunctionSymbol(_name=cls.__INTEGRATE_ODES, _paramTypes=params,
                                _returnType=TypeSymbol.getVoidType(),
                                _elementReference=None, _scope=_scope, _isPredefined=True)
        _scope.addSymbol(symbol)
        return

    final
    MethodSymbol
    i_sum = createFunctionSymbol(CURR_SUM);
    i_sum.addParameterType(getType("pA"));
    i_sum.addParameterType(getRealType());
    i_sum.setReturnType(getType("pA"));
    name2FunctionSymbol.put(CURR_SUM, i_sum);

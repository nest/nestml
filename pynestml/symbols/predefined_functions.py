#
# predefined_functions.py
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
from pynestml.symbols.function_symbol import FunctionSymbol
from pynestml.symbols.predefined_types import PredefinedTypes


class PredefinedFunctions(object):
    """
    This class is used to represent all predefined functions of NESTML.
    
    Attributes:
        TIME_RESOLUTION       The callee name of the resolution function.
        TIME_STEPS            The callee name of the time-steps function.
        EMIT_SPIKE            The callee name of the emit-spike function.
        PRINT                 The callee name of the print function.
        PRINTLN               The callee name of the println function.
        POW                   The callee name of the power function.
        EXP                   The callee name of the exponent function.
        LOG                   The callee name of the logarithm function.
        LOGGER_INFO           The callee name of the logger-info function.
        LOGGER_WARNING        The callee name of the logger-warning function.
        RANDOM                The callee name of the random function.
        RANDOM_INT            The callee name of the random int function.
        EXPM1                 The callee name of the exponent (alternative) function.
        DELTA                 The callee name of the delta function.
        MAX                   The callee name of the max function.
        BOUNDED_MAX           The callee name of the bounded-max function.
        MIN                   The callee name of the min function.
        BOUNDED_MIN           The callee name of the bounded-min function.
        INTEGRATE_ODES        The callee name of the integrate-ode function.
        CURR_SUM              The callee name of the curr-sum function.
        COND_SUM              The callee name of the cond-sum function.
        CONVOLVE              The callee name of the convolve function.
        name2function         A dict of function symbols as currently defined.
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
    DELIVER_SPIKE = 'deliver_spike'
    name2function = {}  # a map dict from function-names to symbols

    @classmethod
    def register_functions(cls):
        """
        Registers all predefined functions.
        """
        cls.name2function = {}
        cls.__register_time_resolution_function()
        cls.__register_time_steps_function()
        cls.__register_emit_spike_function()
        cls.__register_print_function()
        cls.__register_print_ln_function()
        cls.__register_power_function()
        cls.__register_exponent_function()
        cls.__register_log_function()
        cls.__register_logger_info_function()
        cls.__register_logger_warning_function()
        cls.__register_random_function()
        cls.__register_random_int_function()
        cls.__register_exp1_function()
        cls.__register_delta_function()
        cls.__register_max_function()
        cls.__register_max_bounded_function()
        cls.__register_min_function()
        cls.__register_min_bounded_function()
        cls.__register_integrated_odes_function()
        cls.__register_curr_sum_function()
        cls.__register_cond_sum_function()
        cls.__register_convolve()
        cls.__register_deliver_spike()
        return

    @classmethod
    def register_function(cls, name, params, return_type, element_reference):
        symbol = FunctionSymbol(name=name, param_types=params,
                                return_type=return_type,
                                element_reference=element_reference, is_predefined=True)
        cls.name2function[name] = symbol

    @classmethod
    def __register_time_steps_function(cls):
        """
        Registers the time-resolution.
        """
        params = list()
        params.append(PredefinedTypes.get_type('ms'))
        symbol = FunctionSymbol(name=cls.TIME_STEPS, param_types=params,
                                return_type=PredefinedTypes.get_integer_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.TIME_STEPS] = symbol
        return

    @classmethod
    def __register_emit_spike_function(cls):
        """
        Registers the emit-spike function.
        """
        symbol = FunctionSymbol(name=cls.EMIT_SPIKE, param_types=list(),
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.EMIT_SPIKE] = symbol

    @classmethod
    def __register_print_function(cls):
        """
        Registers the print function.
        """
        params = list()
        params.append(PredefinedTypes.get_string_type())
        symbol = FunctionSymbol(name=cls.PRINT, param_types=params,
                                return_type=PredefinedTypes.get_void_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.PRINT] = symbol

    @classmethod
    def __register_print_ln_function(cls):
        """
        Registers the print-line function.
        """
        symbol = FunctionSymbol(name=cls.PRINTLN, param_types=list(),
                                return_type=PredefinedTypes.get_void_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.PRINTLN] = symbol

    @classmethod
    def __register_power_function(cls):
        """
        Registers the power function.
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())  # the base type
        params.append(PredefinedTypes.get_real_type())  # the exponent type
        symbol = FunctionSymbol(name=cls.POW, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.POW] = symbol

    @classmethod
    def __register_exponent_function(cls):
        """
        Registers the exponent (e(X)) function.
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())  # the argument
        symbol = FunctionSymbol(name=cls.EXP, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.EXP] = symbol

    @classmethod
    def __register_log_function(cls):
        """
        Registers the logarithm function (to base 10).
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())  # the argument
        symbol = FunctionSymbol(name=cls.LOG, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.LOG] = symbol

    @classmethod
    def __register_logger_info_function(cls):
        """
        Registers the logger info method into the scope.
        """
        params = list()
        params.append(PredefinedTypes.get_string_type())  # the argument
        symbol = FunctionSymbol(name=cls.LOGGER_INFO, param_types=params,
                                return_type=PredefinedTypes.get_void_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.LOGGER_INFO] = symbol

    @classmethod
    def __register_logger_warning_function(cls):
        """
        Registers the logger warning method.
        """
        params = list()
        params.append(PredefinedTypes.get_string_type())  # the argument
        symbol = FunctionSymbol(name=cls.LOGGER_WARNING, param_types=params,
                                return_type=PredefinedTypes.get_void_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.LOGGER_WARNING] = symbol

    @classmethod
    def __register_random_function(cls):
        """
        Registers the random method as used to generate a random real-typed value.
        """
        symbol = FunctionSymbol(name=cls.RANDOM, param_types=list(),
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.RANDOM] = symbol

    @classmethod
    def __register_random_int_function(cls):
        """
        Registers the random method as used to generate a random integer-typed value.
        """
        symbol = FunctionSymbol(name=cls.RANDOM_INT, param_types=list(),
                                return_type=PredefinedTypes.get_integer_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.RANDOM_INT] = symbol

    @classmethod
    def __register_time_resolution_function(cls):
        """
        Registers the time resolution function.
        """
        symbol = FunctionSymbol(name=cls.TIME_RESOLUTION, param_types=list(),
                                return_type=PredefinedTypes.get_type('ms'),
                                element_reference=None, is_predefined=True, scope=None)
        cls.name2function[cls.TIME_RESOLUTION] = symbol

    @classmethod
    def __register_exp1_function(cls):
        """
        Registers the alternative version of the exponent function, exp1.
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())  # the argument
        symbol = FunctionSymbol(name=cls.EXPM1, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.EXPM1] = symbol

    @classmethod
    def __register_delta_function(cls):
        """
        Registers the delta function.
        """
        params = list()
        params.append(PredefinedTypes.get_type('ms'))
        params.append(PredefinedTypes.get_type('ms'))
        symbol = FunctionSymbol(name=cls.DELTA, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.DELTA] = symbol

    @classmethod
    def __register_max_function(cls):
        """
        Registers the maximum function.
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())
        params.append(PredefinedTypes.get_real_type())
        symbol = FunctionSymbol(name=cls.MAX, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.MAX] = symbol

    @classmethod
    def __register_max_bounded_function(cls):
        """
        Registers the maximum (bounded) function.
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())
        params.append(PredefinedTypes.get_real_type())
        symbol = FunctionSymbol(name=cls.BOUNDED_MAX, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.BOUNDED_MAX] = symbol

    @classmethod
    def __register_min_function(cls):
        """
        Registers the minimum function.
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())
        params.append(PredefinedTypes.get_real_type())
        symbol = FunctionSymbol(name=cls.MIN, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.MIN] = symbol

    @classmethod
    def __register_min_bounded_function(cls):
        """
        Registers the minimum (bounded) function.
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())
        params.append(PredefinedTypes.get_real_type())
        symbol = FunctionSymbol(name=cls.BOUNDED_MIN, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.BOUNDED_MIN] = symbol

    @classmethod
    def __register_integrated_odes_function(cls):
        """
        Registers the integrate-odes function.
        """
        params = list()
        symbol = FunctionSymbol(name=cls.INTEGRATE_ODES, param_types=params,
                                return_type=PredefinedTypes.get_void_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.INTEGRATE_ODES] = symbol

    @classmethod
    def __register_curr_sum_function(cls):
        """
        Registers the curr_sum function into scope.
        """
        params = list()
        params.append(PredefinedTypes.get_type('pA'))
        params.append(PredefinedTypes.get_real_type())
        symbol = FunctionSymbol(name=cls.CURR_SUM, param_types=params,
                                return_type=PredefinedTypes.get_type('pA'),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.CURR_SUM] = symbol

    @classmethod
    def __register_cond_sum_function(cls):
        """
        Registers the cond_sum function into scope.
        """
        params = list()
        params.append(PredefinedTypes.get_type('nS'))
        params.append(PredefinedTypes.get_real_type())
        symbol = FunctionSymbol(name=cls.COND_SUM, param_types=params,
                                return_type=PredefinedTypes.get_type('nS'),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.COND_SUM] = symbol

    @classmethod
    def __register_convolve(cls):
        """
        Registers the convolve function into the system.
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())
        params.append(PredefinedTypes.get_real_type())
        symbol = FunctionSymbol(name=cls.CONVOLVE, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.CONVOLVE] = symbol

    @classmethod
    def __register_deliver_spike(cls):
        """
        Registers the deliver-spike function.
        """
        params = list()
        params.append(PredefinedTypes.get_type('nS'))
        params.append(PredefinedTypes.get_type('ms'))
        symbol = FunctionSymbol(name=cls.DELIVER_SPIKE, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.DELIVER_SPIKE] = symbol

    @classmethod
    def get_function_symbols(cls):
        """
        Returns a copy of the dict containing all predefined functions symbols.
        :return: a copy of the dict containing the functions symbols
        :rtype: dict(FunctionSymbol)
        """
        return cls.name2function

    @classmethod
    def get_function(cls, name):
        """
        Returns a copy of a element in the set of defined functions if one exists, otherwise None
        :param name: the name of the function symbol
        :type name: str
        :return: a copy of the element if such exists in the dict, otherwise None
        :rtype: None or FunctionSymbol
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.SymbolTable.PredefinedFunctions) No or wrong type of name provided (%s)!' % type(name)
        if name in cls.name2function.keys():
            return cls.name2function[name]
        else:
            return None

# -*- coding: utf-8 -*-
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
        EXP                   The callee name of the exponent function.
        LN                    The callee name of the natural logarithm function, i.e. the logarithm function of base :math:`e`.
        LOG10                 The callee name of the logarithm function of base 10.
        COSH                  The callee name of the hyperbolic cosine.
        SINH                  The callee name of the hyperbolic sine.
        TANH                  The callee name of the hyperbolic tangent.
        LOGGER_INFO           The callee name of the logger-info function.
        LOGGER_WARNING        The callee name of the logger-warning function.
        RANDOM_NORMAL         The callee name of the function used to generate a random normal (Gaussian) distributed variable with parameters `mean` and `var` (variance).
        RANDOM_UNIFORM        The callee name of the function used to generate a random sample from a uniform distribution in the interval `[offset, offset + scale)`.
        EXPM1                 The callee name of the exponent (alternative) function.
        DELTA                 The callee name of the delta function.
        CLIP                  The callee name of the clip function.
        MAX                   The callee name of the max function.
        MIN                   The callee name of the min function.
        ABS                   The callee name of the abs function.
        INTEGRATE_ODES        The callee name of the integrate_odes function.
        CONVOLVE              The callee name of the convolve function.
        name2function         A dict of function symbols as currently defined.
    """
    TIME_RESOLUTION = 'resolution'
    TIME_STEPS = 'steps'
    EMIT_SPIKE = 'emit_spike'
    PRINT = 'print'
    PRINTLN = 'println'
    EXP = 'exp'
    LN = 'ln'
    LOG10 = 'log10'
    COSH = 'cosh'
    SINH = 'sinh'
    TANH = 'tanh'
    LOGGER_INFO = 'info'
    LOGGER_WARNING = 'warning'
    RANDOM_NORMAL = 'random_normal'
    RANDOM_UNIFORM = 'random_uniform'
    EXPM1 = 'expm1'
    DELTA = 'delta'
    CLIP = 'clip'
    MAX = 'max'
    MIN = 'min'
    ABS = 'abs'
    INTEGRATE_ODES = 'integrate_odes'
    CONVOLVE = 'convolve'
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
        cls.__register_exponent_function()
        cls.__register_ln_function()
        cls.__register_log10_function()
        cls.__register_cosh_function()
        cls.__register_sinh_function()
        cls.__register_tanh_function()
        cls.__register_logger_info_function()
        cls.__register_logger_warning_function()
        cls.__register_random_normal_function()
        cls.__register_random_uniform_function()
        cls.__register_exp1_function()
        cls.__register_delta_function()
        cls.__register_clip_function()
        cls.__register_max_function()
        cls.__register_min_function()
        cls.__register_abs_function()
        cls.__register_integrated_odes_function()
        cls.__register_convolve()
        return

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
        params = list()
        params.append(PredefinedTypes.get_string_type())
        symbol = FunctionSymbol(name=cls.PRINTLN, param_types=params,
                                return_type=PredefinedTypes.get_void_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.PRINTLN] = symbol

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
    def __register_ln_function(cls):
        """
        Registers the natural logarithm function, i.e. the logarithm function of base :math:`e`.
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())  # the argument
        symbol = FunctionSymbol(name=cls.LN, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.LN] = symbol

    @classmethod
    def __register_log10_function(cls):
        """
        Registers the logarithm function of base 10.
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())  # the argument
        symbol = FunctionSymbol(name=cls.LOG10, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.LOG10] = symbol

    @classmethod
    def __register_cosh_function(cls):
        """
        Registers the hyperbolic cosine function.
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())  # the argument
        symbol = FunctionSymbol(name=cls.COSH, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.COSH] = symbol

    @classmethod
    def __register_sinh_function(cls):
        """
        Registers the hyperbolic sine function.
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())  # the argument
        symbol = FunctionSymbol(name=cls.SINH, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.SINH] = symbol

    @classmethod
    def __register_tanh_function(cls):
        """
        Registers the hyperbolic tangent function.
        """
        params = list()
        params.append(PredefinedTypes.get_real_type())  # the argument
        symbol = FunctionSymbol(name=cls.TANH, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.TANH] = symbol

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
    def __register_random_normal_function(cls):
        """
        Registers the random method as used to generate a random normal (Gaussian) distributed variable with first parameter "mean" and second parameter "standard deviation".
        """
        symbol = FunctionSymbol(name=cls.RANDOM_NORMAL, param_types=[PredefinedTypes.get_template_type(0), PredefinedTypes.get_template_type(0)],
                                return_type=PredefinedTypes.get_template_type(0),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.RANDOM_NORMAL] = symbol

    @classmethod
    def __register_random_uniform_function(cls):
        """
        Registers the random method as used to generate a random sample from a uniform distribution in the interval [offset, offset + scale).
        """
        symbol = FunctionSymbol(name=cls.RANDOM_UNIFORM, param_types=[PredefinedTypes.get_template_type(0), PredefinedTypes.get_template_type(0)],
                                return_type=PredefinedTypes.get_template_type(0),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.RANDOM_UNIFORM] = symbol

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
        symbol = FunctionSymbol(name=cls.DELTA, param_types=params,
                                return_type=PredefinedTypes.get_real_type(),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.DELTA] = symbol

    @classmethod
    def __register_clip_function(cls):
        """
        Registers the clip function (bound a number between a minimum and a
        maximum value).
        """
        params = list()

        params.append(PredefinedTypes.get_template_type(0))  # value
        params.append(PredefinedTypes.get_template_type(0))  # min
        params.append(PredefinedTypes.get_template_type(0))  # max

        symbol = FunctionSymbol(name=cls.CLIP, param_types=params,
                                return_type=PredefinedTypes.get_template_type(0),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.CLIP] = symbol

    @classmethod
    def __register_max_function(cls):
        """
        Registers the maximum function.
        """
        params = list()
        params.append(PredefinedTypes.get_template_type(0))
        params.append(PredefinedTypes.get_template_type(0))
        symbol = FunctionSymbol(name=cls.MAX, param_types=params,
                                return_type=PredefinedTypes.get_template_type(0),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.MAX] = symbol

    @classmethod
    def __register_min_function(cls):
        """
        Registers the minimum function.
        """
        params = list()
        params.append(PredefinedTypes.get_template_type(0))
        params.append(PredefinedTypes.get_template_type(0))
        symbol = FunctionSymbol(name=cls.MIN, param_types=params,
                                return_type=PredefinedTypes.get_template_type(0),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.MIN] = symbol

    @classmethod
    def __register_abs_function(cls):
        """
        Registers the absolute value function.
        """
        params = list()
        params.append(PredefinedTypes.get_template_type(0))
        symbol = FunctionSymbol(name=cls.ABS, param_types=params,
                                return_type=PredefinedTypes.get_template_type(0),
                                element_reference=None, is_predefined=True)
        cls.name2function[cls.ABS] = symbol

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

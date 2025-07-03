# -*- coding: utf-8 -*-
#
# spinnaker_c_function_call_printer.py
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

from pynestml.codegeneration.printers.function_call_printer import FunctionCallPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils


class SpinnakerCFunctionCallPrinter(FunctionCallPrinter):
    r"""
    Printer for ASTFunctionCall in C Spinnaker API  syntax.
    """

#!! function_call was called node before
    def print_function_call(self, function_call: ASTFunctionCall) -> str:
        r"""
        Converts a single handed over function call to C Spinnaker API syntax.

        Parameters
        ----------
        function_call
            The function call node to convert.

        Returns
        -------
        s
            The function call string in C syntax.
        """


        assert isinstance(function_call, ASTFunctionCall)

#taken from previous version of print_function_call()

        if function_call.get_name() in [PredefinedFunctions.TIME_RESOLUTION, PredefinedFunctions.TIME_TIMESTEP]:
            # context dependent; we assume the template contains the necessary definitions
            return 'parameter->__h'

        if function_call.get_name() == PredefinedFunctions.TIME_STEPS:
            raise Exception("time_steps() function not yet implemented")

        if function_call.get_name() == PredefinedFunctions.RANDOM_NORMAL:
            raise Exception("rng functions not yet implemented")

        if function_call.get_name() == PredefinedFunctions.RANDOM_UNIFORM:
            raise Exception("rng functions not yet implemented")

#structure taken from python_function_call_printer.py
        function_name = self._print_function_call_format_string(function_call)


#        import pdb
 #       pdb.set_trace()

        if ASTUtils.needs_arguments(function_call):
            if function_call.get_name() == PredefinedFunctions.PRINT or function_call.get_name() == PredefinedFunctions.PRINT:
                return function_name.format(self._print_print_statement(function_call))

            return function_name.format(*self._print_function_call_argument_list(function_call))

        return function_name




        """ original function
        function_name = node.get_name()

#!!

        import pdb
        pdb.set_trace()


#!! TODO add cases for min and max
        if function_name == PredefinedFunctions.MIN:
            raise Exception("min() not implemented yet")


        if function_name == PredefinedFunctions.MAX:
            raise Exception("max() not implemented yet")

#!! TODO add case for EXP

        if function_name == PredefinedFunctions.EXP:
            raise Exception("exp() not implemented yet")

        if function_name in [PredefinedFunctions.TIME_RESOLUTION, PredefinedFunctions.TIME_TIMESTEP]:
            # context dependent; we assume the template contains the necessary definitions
            return 'parameter->__h'

        if function_name == PredefinedFunctions.TIME_STEPS:
            raise Exception("time_steps() function not yet implemented")

        if function_name == PredefinedFunctions.RANDOM_NORMAL:
            raise Exception("rng functions not yet implemented")

        if function_name == PredefinedFunctions.RANDOM_UNIFORM:
            raise Exception("rng functions not yet implemented")

        return super().print_function_call(node)
    """


#!!
    def _print_function_call_argument_list(self, function_call: ASTFunctionCall) -> tuple[str, ...]:
        ret = []

        for arg in function_call.get_args():
            ret.append(self._expression_printer.print(arg))

        return tuple(ret)


    def _print_function_call_format_string(self, function_call: ASTFunctionCall) -> str:
        r"""
        Converts a single handed over function call to C Spinnaker API syntax.

        Parameters
        ----------
        function_call
            The function call node to convert.

        Returns
        -------
        s
            The function call string in C syntax.
        """

#!!

 #       import pdb
  #      pdb.set_trace()


        function_name = function_call.get_name()

        if function_name == PredefinedFunctions.CLIP:
            # the arguments of this function must be swapped and are therefore [v_max, v_min, v]
            return 'MIN({2!s}, MAX({1!s}, {0!s}))'

        if function_name == PredefinedFunctions.MAX:
            return 'MAX({!s}, {!s})'

        if function_name == PredefinedFunctions.MIN:
            return 'MIN({!s}, {!s})'

        if function_name == PredefinedFunctions.EXP:
            return 'expk({!s})'

        if function_name == PredefinedFunctions.LN:
            return 'logk({!s})'

        if function_name == PredefinedFunctions.POW:
            return '(expk({1!s} * logk({0!s})))'

        if function_name == PredefinedFunctions.LOG10:
            return '(kdivk(logk({!s}), REAL_CONST(2.303)))'

        if function_name == PredefinedFunctions.COS:
            return 'cos({!s})'

        if function_name == PredefinedFunctions.SIN:
            return 'sin({!s})'

        if function_name == PredefinedFunctions.TAN:
            return 'tan({!s})'

        if function_name == PredefinedFunctions.COSH:
            return '(HALF * (expk({!s}) + expk(-{!s})))'

        if function_name == PredefinedFunctions.SINH:
            return '(HALF * (expk({!s}) - expk(-{!s})))'

        if function_name == PredefinedFunctions.TANH:
            return 'kdik((expk({!s}) - expk(-{!s})), (expk({!s}) + expk(-{!s})))'

        if function_name == PredefinedFunctions.ERF:
            raise Exception("Erf not defined for spinnaker")

        if function_name == PredefinedFunctions.ERFC:
            raise Exception("Erfc not defined for spinnaker")

        if function_name == PredefinedFunctions.EXPM1:
            raise Exception("Expm1 not defined for spinnaker")

        if function_name == PredefinedFunctions.PRINT:
            return 'printf("%s", {!s})'

        if function_name == PredefinedFunctions.PRINTLN:
            return 'printf("%s\n",{!s})'

        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            return function_name + '(' + ', '.join(['{!s}' for _ in range(n_args)]) + ')'

        return function_name + '()'

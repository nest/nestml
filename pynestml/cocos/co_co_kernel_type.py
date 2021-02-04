# -*- coding: utf-8 -*-
#
# co_co_kernel_type.py
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

from pynestml.cocos.co_co import CoCo
from pynestml.codegeneration.debug_type_converter import DebugTypeConverter
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.symbols.integer_type_symbol import IntegerTypeSymbol
from pynestml.symbols.real_type_symbol import RealTypeSymbol
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoKernelType(CoCo):
    """
    Ensures that all defined kernels are untyped (for direct functions of time), or have a type equivalent to 1/s**-order, where order is the differential order of the kernel (e.g. 2 for ``kernel g'' = ...``).
    """

    @classmethod
    def check_co_co(cls, node: ASTNeuron):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        kernel_type_visitor = KernelTypeVisitor()
        kernel_type_visitor._neuron = node
        node.accept(kernel_type_visitor)


class KernelTypeVisitor(ASTVisitor):
    """
    This visitor checks if each kernel has the appropriate data type.
    """

    _neuron = None  # the parent ASTNeuron containing the kernel

    def visit_kernel(self, node):
        """
        Checks the coco on the current node.
        :param node: AST kernel object
        :type node: ASTKernel
        """
        for var, expr in zip(node.variables, node.expressions):
            # check kernel type
            if (var.get_differential_order() == 0
                and not type(expr.type) in [IntegerTypeSymbol, RealTypeSymbol]) \
                or (var.get_differential_order() > 0
                    and not expr.type.is_castable_to(PredefinedTypes.get_type("ms")**-var.get_differential_order())):
                actual_type_str = str(expr.type)
                if 'unit' in dir(expr.type) \
                        and expr.type.unit is not None \
                        and expr.type.unit.unit is not None:
                    actual_type_str = str(expr.type.unit.unit)
                code, message = Messages.get_kernel_wrong_type(
                    var.get_name(), var.get_differential_order(), actual_type_str)
                Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                   code=code, message=message)

            # check types of the initial values
            for order in range(var.get_differential_order()):
                iv_name = var.get_name() + order * "'"
                decl = ASTUtils.get_declaration_by_name(self._neuron.get_initial_blocks(), iv_name)
                if decl is None:
                    code, message = Messages.get_variable_not_defined(iv_name)
                    Logger.log_message(node=self._neuron, code=code, message=message, log_level=LoggingLevel.ERROR,
                                       error_position=node.get_source_position())
                    continue
                assert len(self._neuron.get_initial_blocks().get_declarations()[0].get_variables(
                )) == 1, "Only single variables are supported as targets of an assignment."
                iv = decl.get_variables()[0]
                if not iv.get_type_symbol().get_value().is_castable_to(PredefinedTypes.get_type("ms")**-order):
                    actual_type_str = DebugTypeConverter.convert(iv.get_type_symbol())
                    expected_type_str = "s^-" + str(order)
                    code, message = Messages.get_kernel_iv_wrong_type(iv_name, actual_type_str, expected_type_str)
                    Logger.log_message(error_position=node.get_source_position(),
                                       log_level=LoggingLevel.ERROR, code=code, message=message)

# -*- coding: utf-8 -*-
#
# co_co_no_kernels_except_in_convolve.py
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
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoNoKernelsExceptInConvolve(CoCo):
    """
    This CoCo ensures that kernel variables do not occur on the right hand side except in convolve().
    Allowed:
        kernel g_ex = ...
        function I_syn_exc pA = convolve(g_ex, spikeExc) * ( V_m - E_ex )

    Not allowed
        kernel g_ex = ...
        function I_syn_exc pA = g_ex * ( V_m - E_ex )

    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ast_neuron
        """
        kernel_collector_visitor = KernelCollectingVisitor()
        kernel_names = kernel_collector_visitor.collect_kernels(neuron=node)
        kernel_usage_visitor = KernelUsageVisitor(_kernels=kernel_names)
        kernel_usage_visitor.work_on(node)


class KernelUsageVisitor(ASTVisitor):

    def __init__(self, _kernels=None):
        """
        Standard constructor.
        :param _kernels: a list of kernels.
        :type _kernels: list(ASTKernel)
        """
        super(KernelUsageVisitor, self).__init__()
        self.__kernels = _kernels
        self.__neuron_node = None
        return

    def work_on(self, neuron):
        self.__neuron_node = neuron
        neuron.accept(self)
        return

    def visit_variable(self, node: ASTNode):
        """
        Visits each kernel and checks if it is used correctly.
        :param node: a single node.
        :type node: ASTNode
        """
        for kernelName in self.__kernels:
            # in order to allow shadowing by local scopes, we first check if the element has been declared locally
            symbol = node.get_scope().resolve_to_symbol(kernelName, SymbolKind.VARIABLE)
            # if it is not a kernel just continue
            if symbol is None:
                continue
            if not symbol.is_kernel():
                continue
            if node.get_complete_name() == kernelName:
                parent = self.__neuron_node.get_parent(node)
                if parent is not None:
                    if isinstance(parent, ASTKernel):
                        continue
                    grandparent = self.__neuron_node.get_parent(parent)
                    if grandparent is not None and isinstance(grandparent, ASTFunctionCall):
                        grandparent_func_name = grandparent.get_name()
                        if grandparent_func_name == 'convolve':
                            continue
                code, message = Messages.get_kernel_outside_convolve(kernelName)
                Logger.log_message(code=code,
                                   message=message,
                                   log_level=LoggingLevel.ERROR,
                                   error_position=node.get_source_position())


class KernelCollectingVisitor(ASTVisitor):

    def __init__(self):
        super(KernelCollectingVisitor, self).__init__()
        self.kernel_names = None

    def collect_kernels(self, neuron):
        """
        Collects all kernels in the model.
        :param neuron: a single neuron instance
        :type neuron: ast_neuron
        :return: a list of kernels.
        :rtype: list(str)
        """
        self.kernel_names = list()
        neuron.accept(self)
        return self.kernel_names

    def visit_kernel(self, node):
        """
        Collects the kernel.
        :param node: a single kernel node.
        :type node: ASTKernel
        """
        for var in node.get_variables():
            self.kernel_names.append(var.get_name_of_lhs())

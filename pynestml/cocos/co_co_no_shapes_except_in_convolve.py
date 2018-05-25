#
# co_co_no_shapes_except_in_convolve.py
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
from pynestml.meta_model.ast_ode_shape import ASTOdeShape
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoNoShapesExceptInConvolve(CoCo):
    """
    This CoCo ensures that shape variables do not occur on the right hand side except in convolve/curr_sum and
    cond_sum.
    Allowed:
        shape g_ex ...
        function I_syn_exc pA = cond_sum(g_ex, spikeExc) * ( V_m - E_ex )

    Not allowed
        shape g_ex ...
        function I_syn_exc pA = g_ex * ( V_m - E_ex )

    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ast_neuron
        """
        shape_collector_visitor = ShapeCollectingVisitor()
        shape_names = shape_collector_visitor.collect_shapes(neuron=node)
        shape_usage_visitor = ShapeUsageVisitor(_shapes=shape_names)
        shape_usage_visitor.work_on(node)


class ShapeUsageVisitor(ASTVisitor):

    def __init__(self, _shapes=None):
        """
        Standard constructor.
        :param _shapes: a list of shapes.
        :type _shapes: list(ASTOdeShape)
        """
        super(ShapeUsageVisitor, self).__init__()
        self.__shapes = _shapes
        self.__neuron_node = None
        return

    def work_on(self, neuron):
        self.__neuron_node = neuron
        neuron.accept(self)
        return

    def visit_variable(self, node):
        """
        Visits each shape and checks if it is used correctly.
        :param node: a single node.
        :type node: AST_
        """
        for shapeName in self.__shapes:
            # in order to allow shadowing by local scopes, we first check if the element has been declared locally
            symbol = node.get_scope().resolve_to_symbol(shapeName, SymbolKind.VARIABLE)
            # if it is not a shape just continue
            if symbol is None:
                code, message = Messages.get_no_variable_found(shapeName)
                Logger.log_message(neuron=self.__neuron_node, code=code, message=message, log_level=LoggingLevel.ERROR)
                continue
            if not symbol.is_shape():
                continue
            if node.get_complete_name() == shapeName:
                parent = self.__neuron_node.get_parent(node)
                if parent is not None:
                    if isinstance(parent, ASTOdeShape):
                        continue
                    grandparent = self.__neuron_node.get_parent(parent)
                    if grandparent is not None and isinstance(grandparent, ASTFunctionCall):
                        grandparent_func_name = grandparent.get_name()
                        if grandparent_func_name == 'curr_sum' or grandparent_func_name == 'cond_sum' or \
                                grandparent_func_name == 'convolve':
                            continue
                code, message = Messages.get_shape_outside_convolve(shapeName)
                Logger.log_message(error_position=node.get_source_position(),
                                   code=code, message=message,
                                   log_level=LoggingLevel.ERROR)
        return


class ShapeCollectingVisitor(ASTVisitor):

    def __init__(self):
        super(ShapeCollectingVisitor, self).__init__()
        self.shape_names = None

    def collect_shapes(self, neuron):
        """
        Collects all shapes in the model.
        :param neuron: a single neuron instance
        :type neuron: ast_neuron
        :return: a list of shapes.
        :rtype: list(str)
        """
        self.shape_names = list()
        neuron.accept(self)
        return self.shape_names

    def visit_ode_shape(self, node):
        """
        Collects the shape.
        :param node: a single shape node.
        :type node: ASTOdeShape
        """
        self.shape_names.append(node.get_variable().get_name_of_lhs())

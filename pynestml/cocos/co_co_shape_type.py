#
# co_co_shape_type.py
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
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.symbols.integer_type_symbol import IntegerTypeSymbol
from pynestml.symbols.real_type_symbol import RealTypeSymbol
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_types import PredefinedTypes

class CoCoShapeType(CoCo):
    """
    This coco ensures that all defined shapes have type real.
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        node.accept(ShapeTypeVisitor())


class ShapeTypeVisitor(ASTVisitor):
    """
    This visitor checks if each buffer has a datatype selected according to the coco.
    """

    def visit_ode_shape(self, node):
        """
        Checks the coco on the current node.
        :param node: a single input port node.
        :type node: ASTOdeShape
        """
        for var, expr in zip(node.variables, node.expressions):
            if (var.get_differential_order() == 0
                and not type(expr.type) in [IntegerTypeSymbol, RealTypeSymbol]) \
             or (var.get_differential_order() > 0
                 and not expr.type.is_castable_to(PredefinedTypes.get_type("ms")**-(var.get_differential_order()))):
                actual_type_str = str(expr.type)
                if 'unit' in dir(expr.type) \
                 and not expr.type.unit is None \
                 and not expr.type.unit.unit is None:
                    actual_type_str = str(expr.type.unit.unit)
                code, message = Messages.get_shape_wrong_type(var.get_name(), var.get_differential_order(), actual_type_str)
                Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                   code=code, message=message)

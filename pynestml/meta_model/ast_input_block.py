# -*- coding: utf-8 -*-
#
# ast_input_block.py
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

from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_node import ASTNode


class ASTInputBlock(ASTNode):
    """
    This class is used to store blocks of input definitions.
    ASTInputBlock represents the input block, e.g.:
        input:
          spikeBuffer pA <- excitatory spike
          currentBuffer pA <- current
        end

    @attribute inputPort set of input ports.
    Grammar:
          inputBlock: 'input'
            BLOCK_OPEN
              (inputPort | NEWLINE)*
            BLOCK_CLOSE;
    Attributes:
        input_definitions = None
    """

    def __init__(self, input_definitions=None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param input_definitions:
        :type input_definitions: List[ASTInputPort]
        """
        super(ASTInputBlock, self).__init__(*args, **kwargs)
        if input_definitions is None:
            input_definitions = []
        assert (input_definitions is not None and isinstance(input_definitions, list)), \
            '(PyNestML.AST.Input) No or wrong type of input definitions provided (%s)!' % type(input_definitions)
        for definition in input_definitions:
            assert (definition is not None and isinstance(definition, ASTInputPort)), \
                '(PyNestML.AST.Input) No or wrong type of input definition provided (%s)!' % type(definition)
        self.input_definitions = input_definitions

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTInputBlock
        """
        input_definitions_dup = [input_definition.clone() for input_definition in self.input_definitions]
        dup = ASTInputBlock(input_definitions=input_definitions_dup,
                            # ASTNode common attributes:
                            source_position=self.source_position,
                            scope=self.scope,
                            comment=self.comment,
                            pre_comments=[s for s in self.pre_comments],
                            in_comment=self.in_comment,
                            post_comments=[s for s in self.post_comments],
                            implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_input_ports(self):
        """
        Returns the list of input ports.
        :return: a list of input ports
        :rtype: list(ASTInputPort)
        """
        return self.input_definitions

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for port in self.get_input_ports():
            if port is ast:
                return self
            if port.get_parent(ast) is not None:
                return port.get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other:  object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTInputBlock):
            return False
        if len(self.get_input_ports()) != len(other.get_input_ports()):
            return False
        my_input_ports = self.get_input_ports()
        your_input_ports = other.get_input_ports()
        for i in range(0, len(my_input_ports)):
            if not my_input_ports[i].equals(your_input_ports[i]):
                return False
        return True

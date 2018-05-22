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

from pynestml.meta_model.ast_input_line import ASTInputLine
from pynestml.meta_model.ast_node import ASTNode


class ASTInputBlock(ASTNode):
    """
    This class is used to store blocks of input definitions.
    ASTInputBlock represents the input block:
        input:
          spikeBuffer   <- inhibitory excitatory spike
          currentBuffer <- current
        end

    @attribute inputLine set of input lines.
    Grammar:
          inputBlock: 'input'
            BLOCK_OPEN
              (inputLine | NEWLINE)*
            BLOCK_CLOSE;
    """
    __inputDefinitions = None

    def __init__(self, input_definitions=list(), source_position=None):
        """
        Standard constructor.
        :param input_definitions:
        :type input_definitions: list(ASTInputLine)
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        """
        assert (input_definitions is not None and isinstance(input_definitions, list)), \
            '(PyNestML.AST.Input) No or wrong type of input definitions provided (%s)!' % type(input_definitions)
        for definition in input_definitions:
            assert (definition is not None and isinstance(definition, ASTInputLine)), \
                '(PyNestML.AST.Input) No or wrong type of input definition provided (%s)!' % type(definition)
        super(ASTInputBlock, self).__init__(source_position)
        self.__inputDefinitions = input_definitions
        return

    def get_input_lines(self):
        """
        Returns the list of input lines.
        :return: a list of input lines
        :rtype: list(ASTInputLine)
        """
        return self.__inputDefinitions

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for line in self.get_input_lines():
            if line is ast:
                return self
            elif line.get_parent(ast) is not None:
                return line.get_parent(ast)
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
        if len(self.get_input_lines()) != len(other.get_input_lines()):
            return False
        my_input_lines = self.get_input_lines()
        your_input_lines = other.get_input_lines()
        for i in range(0, len(my_input_lines)):
            if not my_input_lines[i].equals(your_input_lines[i]):
                return False
        return True

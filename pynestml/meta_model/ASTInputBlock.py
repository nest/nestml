#
# ASTInputBlock.py
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

from pynestml.meta_model.ASTInputLine import ASTInputLine
from pynestml.meta_model.ASTNode import ASTNode


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

    def __init__(self, _inputDefinitions=list(), source_position=None):
        """
        Standard constructor.
        :param _inputDefinitions: 
        :type _inputDefinitions: list(ASTInputLine)
        :param source_position: the position of this element in the source file.
        :type _sourcePosition: ASTSourceLocation.
        """
        assert (_inputDefinitions is not None and isinstance(_inputDefinitions, list)), \
            '(PyNestML.AST.Input) No or wrong type of input definitions provided (%s)!' % type(_inputDefinitions)
        for definition in _inputDefinitions:
            assert (definition is not None and isinstance(definition, ASTInputLine)), \
                '(PyNestML.AST.Input) No or wrong type of input definition provided (%s)!' % type(definition)
        super(ASTInputBlock, self).__init__(source_position)
        self.__inputDefinitions = _inputDefinitions
        return

    def getInputLines(self):
        """
        Returns the list of input lines.
        :return: a list of input lines
        :rtype: list(ASTInputLine)
        """
        return self.__inputDefinitions

    def get_parent(self, ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for line in self.getInputLines():
            if line is ast:
                return self
            elif line.get_parent(ast) is not None:
                return line.get_parent(ast)
        return None

    def equals(self, other=None):
        """
        The equals method.
        :param other: a different object.
        :type other:  object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTInputBlock):
            return False
        if len(self.getInputLines()) != len(other.getInputLines()):
            return False
        my_input_lines = self.getInputLines()
        your_input_lines = other.getInputLines()
        for i in range(0, len(my_input_lines)):
            if not my_input_lines[i].equals(your_input_lines[i]):
                return False
        return True

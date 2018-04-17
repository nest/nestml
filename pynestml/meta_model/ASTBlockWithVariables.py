#
# ASTBlockWithVariables.py
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


from pynestml.meta_model.ASTNode import ASTNode


class ASTBlockWithVariables(ASTNode):
    """
    This class is used to store a block of variable declarations.
    ASTBlockWithVariables.py represent a block with variables, e.g.:
        state:
          y0, y1, y2, y3 mV [y1 > 0; y2 > 0]
        end

    attribute state true: if the varblock is a state.
    attribute parameter: true if the varblock is a parameter.
    attribute internal: true if the varblock is a state internal.
    attribute AliasDecl: a list with variable declarations
    Grammar:
         blockWithVariables:
            blockType=('state'|'parameters'|'internals'|'initial_values')
            BLOCK_OPEN
              (declaration | NEWLINE)*
            BLOCK_CLOSE;
    """
    __isState = False
    __isParameters = False
    __isInternals = False
    __isInitValues = False
    __declarations = None

    def __init__(self, is_state=False, is_parameters=False, is_internals=False, is_initial_values=False,
                 declarations=list(), source_position=None):
        """
        Standard constructor.
        :param is_state: is a state block.
        :type is_state: bool
        :param is_parameters: is a parameter block.
        :type is_parameters: bool 
        :param is_internals: is an internals block.
        :type is_internals: bool
        :param is_initial_values: is an initial values block.
        :type is_initial_values: bool
        :param declarations: a list of declarations.
        :type declarations: list(ASTDeclaration)
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        """
        assert (is_internals or is_parameters or is_state or is_initial_values), \
            '(PyNESTML.AST.BlockWithVariables) Type of variable block specified!'
        assert ((is_internals + is_parameters + is_state + is_initial_values) == 1), \
            '(PyNestML.AST.BlockWithVariables) Type of block ambiguous!'
        assert (declarations is None or isinstance(declarations, list)), \
            '(PyNESTML.AST.BlockWithVariables) Wrong type of declaration provided (%s)!' % type(declarations)
        super(ASTBlockWithVariables, self).__init__(source_position)
        self.__declarations = declarations
        self.__isInternals = is_internals
        self.__isParameters = is_parameters
        self.__isInitValues = is_initial_values
        self.__isState = is_state
        return

    def is_state(self):
        """
        Returns whether it is a state block or not.
        :return: True if state block, otherwise False.
        :rtype: bool
        """
        return self.__isState

    def is_parameters(self):
        """
        Returns whether it is a parameters block or not.
        :return: True if parameters block, otherwise False.
        :rtype: bool
        """
        return self.__isParameters

    def is_internals(self):
        """
        Returns whether it is an internals block or not.
        :return: True if internals block, otherwise False.
        :rtype: bool
        """
        return self.__isInternals

    def is_initial_values(self):
        """
        Returns whether it is a initial-values block.
        :return: True if initial values block, otherwise False.
        :rtype: bool
        """
        return self.__isInitValues

    def get_declarations(self):
        """
        Returns the set of stored declarations.
        :return: set of declarations
        :rtype: set(ASTDeclaration)
        """
        return self.__declarations

    def clear(self):
        """
        Clears the list of declarations in this block.
        """
        del self.__declarations
        self.__declarations = list()
        return

    def get_parent(self, ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for stmt in self.get_declarations():
            if stmt is ast:
                return self
            if stmt.get_parent(ast) is not None:
                return stmt.get_parent(ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the variable block.
        :return: a string representation
        :rtype: str
        """
        ret = ''
        if self.is_state():
            ret += 'state'
        elif self.is_parameters():
            ret += 'parameters'
        elif self.is_internals():
            ret += 'internals'
        else:
            ret += 'initial_values'
        ret += ':\n'
        if self.get_declarations() is not None:
            for decl in self.get_declarations():
                ret += str(decl) + '\n'
        ret += 'end'
        return ret

    def equals(self, other=None):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False
        :rtype: bool
        """
        if not isinstance(other, ASTBlockWithVariables):
            return False
        if not (self.is_initial_values() == other.is_initial_values()
                and self.is_internals() == other.is_internals() and
                self.is_parameters() == other.is_parameters() and self.is_state() == other.is_state()):
            return False
        if len(self.get_declarations()) != len(other.get_declarations()):
            return False
        my_declarations = self.get_declarations()
        your_declarations = other.get_declarations()
        for i in range(0, len(my_declarations)):
            if not my_declarations[i].equals(your_declarations[i]):
                return False
        return True

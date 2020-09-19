# -*- coding: utf-8 -*-
#
# ast_block_with_variables.py
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

from pynestml.meta_model.ast_node import ASTNode


class ASTBlockWithVariables(ASTNode):
    """
    This class is used to store a block of variable declarations.
    ast_block_with_variables.py represent a block with variables, e.g.:
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
    Attributes:
        is_state = False
        is_parameters = False
        is_internals = False
        is_initial_values = False
        declarations = None
    """

    def __init__(self, is_state=False, is_parameters=False, is_internals=False, is_initial_values=False,
                 declarations=None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param is_state: is a state block.
        :type is_state: bool
        :param is_parameters: is a parameter block.
        :type is_parameters: bool
        :param is_internals: is an internals block.
        :type is_internals: bool
        :param is_initial_values: is an initial values block.
        :type is_initial_values: bool
        :param declarations: a list of declarations.
        :type declarations: List[ASTDeclaration]
        """
        super(ASTBlockWithVariables, self).__init__(*args, **kwargs)
        assert (is_internals or is_parameters or is_state or is_initial_values), \
            '(PyNESTML.AST.BlockWithVariables) Type of variable block specified!'
        assert ((is_internals + is_parameters + is_state + is_initial_values) == 1), \
            '(PyNestML.AST.BlockWithVariables) Type of block ambiguous!'
        assert (declarations is None or isinstance(declarations, list)), \
            '(PyNESTML.AST.BlockWithVariables) Wrong type of declaration provided (%s)!' % type(declarations)
        self.declarations = declarations
        self.is_internals = is_internals
        self.is_parameters = is_parameters
        self.is_initial_values = is_initial_values
        self.is_state = is_state

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTBlockWithVariables
        """
        declarations_dup = None
        if self.declarations:
            declarations_dup = [decl.clone() for decl in self.declarations]
        dup = ASTBlockWithVariables(declarations=declarations_dup,
                                    is_internals=self.is_internals,
                                    is_parameters=self.is_parameters,
                                    is_initial_values=self.is_initial_values,
                                    is_state=self.is_state,
                                    # ASTNode common attriutes:
                                    source_position=self.source_position,
                                    scope=self.scope,
                                    comment=self.comment,
                                    pre_comments=[s for s in self.pre_comments],
                                    in_comment=self.in_comment,
                                    post_comments=[s for s in self.post_comments],
                                    implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_declarations(self):
        """
        Returns the set of stored declarations.
        :return: set of declarations
        :rtype: set(ASTDeclaration)
        """
        return self.declarations

    def clear(self):
        """
        Clears the list of declarations in this block.
        """
        del self.declarations
        self.declarations = list()

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
        if not (self.is_initial_values == other.is_initial_values
                and self.is_internals == other.is_internals
                and self.is_parameters == other.is_parameters and self.is_state == other.is_state):
            return False
        if len(self.get_declarations()) != len(other.get_declarations()):
            return False
        my_declarations = self.get_declarations()
        your_declarations = other.get_declarations()
        for i in range(0, len(my_declarations)):
            if not my_declarations[i].equals(your_declarations[i]):
                return False
        return True

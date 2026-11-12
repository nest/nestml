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

from __future__ import annotations

from typing import List, Optional

from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_node import ASTNode


class ASTBlockWithVariables(ASTNode):
    r"""
    This class is used to store a block of variable declarations, for example, the state, parameters and internals blocks.
    """

    def __init__(self, is_state: bool = False, is_parameters: bool = False, is_internals: bool = False, declarations: Optional[List[ASTDeclaration]] = None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param is_state: is a state block.
        :param is_parameters: is a parameter block.
        :param is_internals: is an internals block.
        :param declarations: a list of declarations.
        """
        super(ASTBlockWithVariables, self).__init__(*args, **kwargs)

        assert (is_internals or is_parameters or is_state), "Type of variable block not specified!"
        assert ((is_internals + is_parameters + is_state) == 1), "Type of block ambiguous!"

        if declarations is None:
            self.declarations = []
        else:
            self.declarations = declarations

        self.is_internals = is_internals
        self.is_parameters = is_parameters
        self.is_state = is_state

    def clone(self) -> ASTBlockWithVariables:
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        """
        declarations_dup = [decl.clone() for decl in self.declarations]
        dup = ASTBlockWithVariables(declarations=declarations_dup,
                                    is_internals=self.is_internals,
                                    is_parameters=self.is_parameters,
                                    is_state=self.is_state,
                                    # ASTNode common attriutes:
                                    source_position=self.source_position,
                                    scope=self.scope,
                                    comment=self.comment,
                                    pre_comments=[s for s in self.pre_comments],
                                    in_comment=self.in_comment,
                                    implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_declarations(self) -> List[ASTDeclaration]:
        """
        Returns the set of stored declarations.
        :return: set of declarations
        """
        return self.declarations

    def clear(self):
        """
        Clears the list of declarations in this block.
        """
        del self.declarations
        self.declarations = list()

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        return self.get_declarations()

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTBlockWithVariables):
            return False
        if not (self.is_internals == other.is_internals
                and self.is_parameters == other.is_parameters
                and self.is_state == other.is_state):
            return False
        if len(self.get_declarations()) != len(other.get_declarations()):
            return False
        my_declarations = self.get_declarations()
        your_declarations = other.get_declarations()
        for i in range(0, len(my_declarations)):
            if not my_declarations[i].equals(your_declarations[i]):
                return False
        return True

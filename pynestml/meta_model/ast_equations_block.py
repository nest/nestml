# -*- coding: utf-8 -*-
#
# ast_equations_block.py
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
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_kernel import ASTKernel


class ASTEquationsBlock(ASTNode):
    """
    This class is used to store an equations block.
    ASTEquationsBlock a special function definition:
       equations:
         G = (e/tau_syn) * t * exp(-1/tau_syn*t)
         V' = -1/Tau * V + 1/C_m * (convolve(G, spikes) + I_e + I_stim)
       end
     @attribute odeDeclaration Block with equations and differential equations.
     Grammar:
          equationsBlock:
            'equations'
            BLOCK_OPEN
              (inlineExpression | odeEquation | kernel | NEWLINE)+
            BLOCK_CLOSE;
    Attributes:
        declarations = None
    """

    def __init__(self, declarations, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param declarations: a block of definitions.
        :type declarations: ast_block
        """
        assert (declarations is not None and isinstance(declarations, list)), \
            '(PyNestML.AST.EquationsBlock) No or wrong type of declarations provided (%s)!' % type(declarations)
        for decl in declarations:
            assert (decl is not None and (isinstance(decl, ASTKernel)
                                          or isinstance(decl, ASTOdeEquation)
                                          or isinstance(decl, ASTInlineExpression))), \
                '(PyNestML.AST.EquationsBlock) No or wrong type of ode-element provided (%s)' % type(decl)
        super(ASTEquationsBlock, self).__init__(*args, **kwargs)
        self.declarations = declarations

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTEquationsBlock
        """
        declarations_dup = None
        if self.declarations:
            declarations_dup = [decl.clone() for decl in self.declarations]
        dup = ASTEquationsBlock(declarations=declarations_dup,
                                # ASTNode common attributes:
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
        Returns the block of definitions.
        :return: the block
        :rtype: list(ASTInlineExpression|ASTOdeEquation|ASTKernel)
        """
        return self.declarations

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for decl in self.get_declarations():
            if decl is ast:
                return self
            if decl.get_parent(ast) is not None:
                return decl.get_parent(ast)
        return None

    def get_ode_equations(self):
        """
        Returns a list of all ode equations in this block.
        :return: a list of all ode equations.
        :rtype: list(ASTOdeEquations)
        """
        ret = list()
        for decl in self.get_declarations():
            if isinstance(decl, ASTOdeEquation):
                ret.append(decl)
        return ret

    def get_kernels(self):
        """
        Returns a list of all kernels in this block.
        :return: a list of all kernels.
        :rtype: list(ASTKernel)
        """
        ret = list()
        for decl in self.get_declarations():
            if isinstance(decl, ASTKernel):
                ret.append(decl)
        return ret

    def get_inline_expressions(self):
        """
        Returns a list of all inline expressions in this block.
        :return: a list of all inline expressions.
        :rtype: list(ASTInlineExpression)
        """
        ret = list()
        for decl in self.get_declarations():
            if isinstance(decl, ASTInlineExpression):
                ret.append(decl)
        return ret

    def clear(self):
        """
        Deletes all declarations as stored in this block.
        """
        del self.declarations
        self.declarations = list()

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTEquationsBlock):
            return False
        if len(self.get_declarations()) != len(other.get_declarations()):
            return False
        my_declarations = self.get_declarations()
        your_declarations = other.get_declarations()
        for i in range(0, len(my_declarations)):
            if not my_declarations[i].equals(your_declarations[i]):
                return False
        return True

# -*- coding: utf-8 -*-
#
# ast_synapse_body.py
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

from typing import List, Optional

from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_on_receive_block import ASTOnReceiveBlock

class ASTSynapseBody(ASTNode):
    """
    ...
    """

    def __init__(self, synapse_body_elements, *args, **kwargs):
        """
        Standard constructor.
        :param body_elements: a list of elements, e.g. variable blocks.
        :type body_elements: list()
        :param source_position: the position of the element in the source model
        :rtype source_location: ASTSourceLocation
        """
        super(ASTSynapseBody, self).__init__(*args, **kwargs)
        self.synapseBodyElements = synapse_body_elements

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTNeuronBody
        """
        body_elements_dup = None
        if self.synapseBodyElements:
            body_elements_dup = [body_element.clone() for body_element in self.synapseBodyElements]
        dup = ASTSynapseBody(synapse_body_elements=body_elements_dup,
                             # ASTNode common attriutes:
                             source_position=self.source_position,
                             scope=self.scope,
                             comment=self.comment,
                             pre_comments=[s for s in self.pre_comments],
                             in_comment=self.in_comment,
                             post_comments=[s for s in self.post_comments],
                             implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_body_elements(self):
        """
        Returns the list of body elements.
        :return: a list of body elements.
        :rtype: list()
        """
        return self.synapseBodyElements

    # def get_functions(self):
    #     """
    #     Returns a list of all function block declarations in this body.
    #     :return: a list of function declarations.
    #     :rtype: list(ASTFunction)
    #     """
    #     ret = list()
    #     from pynestml.meta_model.ast_function import ASTFunction
    #     for elem in self.get_body_elements():
    #         if isinstance(elem, ASTFunction):
    #             ret.append(elem)
    #     return ret

    def get_update_blocks(self):
        """
        Returns a list of all update blocks defined in this body.
        :return: a list of update-block elements.
        :rtype: list(ASTUpdateBlock)
        """
        ret = list()
        from pynestml.meta_model.ast_update_block import ASTUpdateBlock
        for elem in self.get_body_elements():
            if isinstance(elem, ASTUpdateBlock):
                ret.append(elem)
        return ret

    # def get_state_blocks(self):
    #     """
    #     Returns a list of all state blocks defined in this body.
    #     :return: a list of state-blocks.
    #     :rtype: list(ASTBlockWithVariables)
    #     """
    #     ret = list()
    #     from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
    #     for elem in self.get_body_elements():
    #         if isinstance(elem, ASTBlockWithVariables) and elem.is_state:
    #             ret.append(elem)
    #     return ret

    def get_parameter_blocks(self):
        """
        Returns a list of all parameter blocks defined in this body.
        :return: a list of parameters-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        for elem in self.get_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_parameters:
                ret.append(elem)
        return ret

    def get_internals_blocks(self):
        """
        Returns a list of all internals blocks defined in this body.
        :return: a list of internals-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        for elem in self.get_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_internals:
                ret.append(elem)
        return ret

    def get_on_receive_block(self, port_name) -> Optional[ASTOnReceiveBlock]:
        for elem in self.get_body_elements():
            if isinstance(elem, ASTOnReceiveBlock) and elem.port_name == port_name:
                return elem
        return None

    def get_on_receive_blocks(self) -> List[ASTOnReceiveBlock]:
        on_receive_blocks = []
        for elem in self.get_body_elements():
            if isinstance(elem, ASTOnReceiveBlock):
                on_receive_blocks.append(elem)
        return on_receive_blocks

    def get_equations_blocks(self):
        """
        Returns a list of all equations blocks defined in this body.
        :return: a list of equations-blocks.
        :rtype: list(ASTEquationsBlock)
        """
        ret = list()
        from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
        for elem in self.get_body_elements():
            if isinstance(elem, ASTEquationsBlock):
                ret.append(elem)
        return ret

    def get_input_blocks(self):
        """
        Returns a list of all input-blocks defined.
        :return: a list of defined input-blocks.
        :rtype: list(ASTInputBlock)
        """
        ret = list()
        from pynestml.meta_model.ast_input_block import ASTInputBlock
        for elem in self.get_body_elements():
            if isinstance(elem, ASTInputBlock):
                ret.append(elem)
        return ret

    def get_output_blocks(self):
        """
        Returns a list of all output-blocks defined.
        :return: a list of defined output-blocks.
        :rtype: list(ASTOutputBlock)
        """
        ret = list()
        from pynestml.meta_model.ast_output_block import ASTOutputBlock
        for elem in self.get_body_elements():
            if isinstance(elem, ASTOutputBlock):
                ret.append(elem)
        return ret

    def get_parent(self, ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for stmt in self.get_body_elements():
            if stmt is ast:
                return self
            if stmt.get_parent(ast) is not None:
                return stmt.get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTSynapseBody):
            return False
        if len(self.get_body_elements()) != len(other.get_body_elements()):
            return False
        my_synapse_body_elements = self.get_body_elements()
        your_synapse_body_elements = other.get_body_elements()
        for i in range(0, len(my_synapse_body_elements)):
            if not my_synapse_body_elements[i].equals(your_synapse_body_elements[i]):
                return False
        return True

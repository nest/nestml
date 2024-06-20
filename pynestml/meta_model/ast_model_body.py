# -*- coding: utf-8 -*-
#
# ast_model_body.py
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

from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_input_block import ASTInputBlock
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_on_condition_block import ASTOnConditionBlock
from pynestml.meta_model.ast_on_receive_block import ASTOnReceiveBlock
from pynestml.meta_model.ast_output_block import ASTOutputBlock
from pynestml.meta_model.ast_update_block import ASTUpdateBlock


class ASTModelBody(ASTNode):
    """
    This class is used to store the body of a neuron or synapse, an object containing all the definitions.
    ASTModelBody The body of the neuron, e.g. internal, state, parameter...
    Grammar:
        body : BLOCK_OPEN
               (NEWLINE | blockWithVariables | updateBlock | equationsBlock | inputBlock | outputBlock | function)*
               BLOCK_CLOSE;
    Attributes:
        body_elements = None
    """

    def __init__(self, body_elements, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param body_elements: a list of elements, e.g. variable blocks.
        :type body_elements: List[ASTNode]
        """
        super(ASTModelBody, self).__init__(*args, **kwargs)
        self.body_elements = body_elements

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTModelBody
        """
        body_elements_dup = None
        if self.body_elements:
            body_elements_dup = [body_element.clone() for body_element in self.body_elements]
        dup = ASTModelBody(body_elements=body_elements_dup,
                           # ASTNode common attriutes:
                           source_position=self.source_position,
                           scope=self.scope,
                           comment=self.comment,
                           pre_comments=[s for s in self.pre_comments],
                           in_comment=self.in_comment,
                           implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_body_elements(self):
        """
        Returns the list of body elements.
        :return: a list of body elements.
        :rtype: list()
        """
        return self.body_elements

    def get_functions(self):
        """
        Returns a list of all function block declarations in this body.
        :return: a list of function declarations.
        :rtype: list(ASTFunction)
        """
        ret = list()
        from pynestml.meta_model.ast_function import ASTFunction
        for elem in self.get_body_elements():
            if isinstance(elem, ASTFunction):
                ret.append(elem)
        return ret

    def get_update_blocks(self) -> List[ASTUpdateBlock]:
        """
        Returns a list of all update blocks defined in this body.
        :return: a list of update-block elements.
        """
        ret = list()
        for elem in self.get_body_elements():
            if isinstance(elem, ASTUpdateBlock):
                ret.append(elem)

        return ret

    def get_state_blocks(self) -> List[ASTBlockWithVariables]:
        """
        Returns a list of all state blocks defined in this body.
        :return: a list of state-blocks.
        """
        ret = list()
        for elem in self.get_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_state:
                ret.append(elem)

        return ret

    def get_parameters_blocks(self) -> List[ASTBlockWithVariables]:
        """
        Returns a list of all parameter blocks defined in this body.
        :return: a list of parameters-blocks.
        """
        ret = list()
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        for elem in self.get_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_parameters:
                ret.append(elem)

        return ret

    def get_internals_blocks(self) -> List[ASTBlockWithVariables]:
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
        """Returned blocks are sorted descending, from high priority to low priority, if priority options were specified."""
        on_receive_blocks = []
        priority_to_receive_block = {None: []}  # None for no priority specified
        for elem in self.get_body_elements():
            if isinstance(elem, ASTOnReceiveBlock):
                if "priority" in elem.get_const_parameters():
                    priority_to_receive_block[elem.get_const_parameters()["priority"]] = elem
                else:
                    priority_to_receive_block[None].append(elem)

        keys = [k for k in priority_to_receive_block.keys() if not k is None]

        for k in sorted(keys, reverse=True):
            on_receive_blocks.append(priority_to_receive_block[k])

        on_receive_blocks.extend(priority_to_receive_block[None])

        return on_receive_blocks

    def get_on_condition_block(self, port_name) -> Optional[ASTOnConditionBlock]:
        for elem in self.get_body_elements():
            if isinstance(elem, ASTOnConditionBlock) and elem.port_name == port_name:
                return elem
        return None

    def get_on_condition_blocks(self) -> List[ASTOnConditionBlock]:
        on_condition_blocks = []
        for elem in self.get_body_elements():
            if isinstance(elem, ASTOnConditionBlock):
                on_condition_blocks.append(elem)
        return on_condition_blocks

    def get_equations_blocks(self) -> List[ASTEquationsBlock]:
        """
        Returns a list of all equations blocks defined in this body.
        :return: a list of equations-blocks.
        """
        ret = list()
        for elem in self.get_body_elements():
            if isinstance(elem, ASTEquationsBlock):
                ret.append(elem)

        return ret

    def get_input_blocks(self) -> List[ASTInputBlock]:
        """
        Returns a list of all input-blocks defined.
        :return: a list of defined input-blocks.
        """
        ret = list()
        for elem in self.get_body_elements():
            if isinstance(elem, ASTInputBlock):
                ret.append(elem)

        return ret

    def get_output_blocks(self) -> List[ASTOutputBlock]:
        """
        Returns a list of all output-blocks defined.
        :return: a list of defined output-blocks.
        :rtype: list(ASTOutputBlock)
        """
        ret = list()
        for elem in self.get_body_elements():
            if isinstance(elem, ASTOutputBlock):
                ret.append(elem)

        return ret

    def get_spike_input_ports(self) -> List[ASTInputPort]:
        """
        Returns a list of all spike input ports defined in the model.
        :return: a list of all spike input ports
        """
        ret = list()
        blocks = self.get_input_blocks()
        for block in blocks:
            for port in block.get_input_ports():
                if port.is_spike():
                    ret.append(port)
        return ret

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        return self.get_body_elements()

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTModelBody):
            return False
        if len(self.get_body_elements()) != len(other.get_body_elements()):
            return False
        my_body_elements = self.get_body_elements()
        your_body_elements = other.get_body_elements()
        for i in range(0, len(my_body_elements)):
            if not my_body_elements[i].equals(your_body_elements[i]):
                return False
        return True

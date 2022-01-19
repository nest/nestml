# -*- coding: utf-8 -*-
#
# ast_input_qualifier.py
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

from typing import Any, Optional

import enum

from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.port_qualifier_type import PortQualifierType


class ASTInputQualifier(ASTNode):
    """
    This class is used to store the qualifier of a buffer.
    ASTInputQualifier represents the qualifier of the input port. Only valid for spiking inputs.

    Grammar:
        inputQualifier : (isInhibitory=INHIBITORY_KEYWORD
                            | isExcitatory=EXCITATORY_KEYWORD
                            | isPre=PRE_KEYWORD
                            | isPost=POST_KEYWORD
                            | isMod=MOD_KEYWORD);
    Attributes:
        qualifier_type : PortQualifierType
    """

    def __init__(self, qualifier_type: PortQualifierType, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        qualifier_type
            Represents the qualifier of the input port.
        """
        super(ASTInputQualifier, self).__init__(*args, **kwargs)
        self.qualifier_type = qualifier_type

    def clone(self) -> ASTInputQualifier:
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        """
        dup = ASTInputQualifier(qualifier_type=self.qualifier_type,
                                # ASTNode common attributes:
                                source_position=self.source_position,
                                scope=self.scope,
                                comment=self.comment,
                                pre_comments=[s for s in self.pre_comments],
                                in_comment=self.in_comment,
                                post_comments=[s for s in self.post_comments],
                                implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_parent(self, ast: ASTNode) -> Optional[ASTNode]:
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :return: AST if this or one of the child nodes contains the handed over element.
        """
        return None

    def equals(self, other: Any) -> bool:
        """
        The equals method.
        :param other: a different object.
        :return: True if equal, otherwise False.
        """
        if not isinstance(other, ASTInputQualifier):
            return False
        return self.qualifier_type == other.qualifier_type

    def get_qualifier_type(self) -> PortQualifierType:
        return self.qualifier_type

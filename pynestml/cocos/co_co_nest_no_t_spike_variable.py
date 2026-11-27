# -*- coding: utf-8 -*-
#
# co_co_nest_no_t_spike_variable.py
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

from typing import Any, Dict, Optional

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoNESTNoTSpikeVariable(CoCo):
    r"""
    This coco checks that no variable (state variable, parameter, internal, local variable or inline expression) in a neuron model is named ``t_spike``.

    In NEST Simulator, ``t_spike`` is a reserved name in the status dictionary of a neuron (it is used by ``ArchivingNode`` to report the time of the last emitted spike). A NESTML variable of the same name would be overwritten in the status dictionary when reading it out using ``GetStatus()``.

    This coco is only checked for neuron models; synapses do not have this restriction. (When generating code for neuron-synapse pairs, synapse variables that are moved into the neuron are renamed with a ``__for_<synapse name>`` suffix, so they cannot collide either.)
    """

    reserved_name = "t_spike"

    @classmethod
    @override
    def check_co_co(cls, node: ASTNode, metadata: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Ensures the coco for the handed over model.
        :param node: a single model instance.
        """
        assert isinstance(node, ASTModel), "This coco can only be called on ASTModels!"
        node.accept(CoCoNESTNoTSpikeVariableVisitor())


class CoCoNESTNoTSpikeVariableVisitor(ASTVisitor):
    def visit_declaration(self, node: ASTDeclaration) -> None:
        for variable in node.get_variables():
            if variable.get_name() == CoCoNESTNoTSpikeVariable.reserved_name:
                self._log_error(node)

    def visit_inline_expression(self, node: ASTInlineExpression) -> None:
        if node.get_variable_name() == CoCoNESTNoTSpikeVariable.reserved_name:
            self._log_error(node)

    def _log_error(self, node: ASTNode) -> None:
        code, message = Messages.get_nest_t_spike_variable(CoCoNESTNoTSpikeVariable.reserved_name)
        Logger.log_message(error_position=node.get_source_position(),
                           code=code, message=message,
                           log_level=LoggingLevel.ERROR)

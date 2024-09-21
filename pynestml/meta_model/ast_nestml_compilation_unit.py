# -*- coding: utf-8 -*-
#
# ast_nestml_compilation_unit.py
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

from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode


class ASTNestMLCompilationUnit(ASTNode):
    """
    Store a collection of processed ASTModels.
    """

    def __init__(self, model_list: List[ASTModel] = None, artifact_name=None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param model_list: list of contained neurons
        :param artifact_name: the name of the file where ths model is contained in
        """
        super(ASTNestMLCompilationUnit, self).__init__(*args, **kwargs)
        assert (artifact_name is not None and isinstance(artifact_name, str)), \
            '(PyNestML.AST.NestMLCompilationUnit) No or wrong type of artifact name provided (%s)!' % type(artifact_name)
        self.model_list = []
        if model_list is not None:
            assert type(model_list) is list
            self.model_list.extend(model_list)
        self.artifact_name = artifact_name

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTNestMLCompilationUnit
        """
        model_list_dup = [neuron.clone() for neuron in self.model_list]
        dup = ASTNestMLCompilationUnit(artifact_name=self.artifact_name,
                                       model_list=model_list_dup,
                                       # ASTNode common attributes:
                                       source_position=self.source_position,
                                       scope=self.scope,
                                       comment=self.comment,
                                       pre_comments=[s for s in self.pre_comments],
                                       in_comment=self.in_comment,
                                       implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def add_model(self, model: ASTModel):
        """
        Expects an instance of a model which is added to the collection.
        :param neuron: an instance of a model
        """
        assert (model is not None and isinstance(model, ASTModel)), \
            '(PyNestML.AST.CompilationUnit) No or wrong type of model provided (%s)!' % type(model)
        self.model_list.append(model)

    def delete_model(self, model: ASTModel) -> bool:
        """
        Expects an instance of a model which is deleted from the collection.
        :param model: an instance
        :return: True if element deleted from list, False else.
        """
        if self.model_list.__contains__(model):
            self.model_list.remove(model)
            return True
        return False

    def get_model_list(self):
        """
        :return: a list of neuron elements as stored in the unit
        :rtype: list(ASTModel)
        """
        return self.model_list

    def get_model_by_name(self, name: str) -> Optional[ASTModel]:
        for model in self.get_model_list():
            if model.get_name() == name:
                return model

        return None

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        return self.get_model_list()

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTNestMLCompilationUnit):
            return False
        if len(self.get_model_list()) != len(other.get_model_list()):
            return False
        my_models = self.get_model_list()
        your_models = other.get_model_list()
        for i in range(0, len(my_models)):
            if not my_models[i].equals(your_models[i]):
                return False
        return True

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

from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_node import ASTNode


class ASTNestMLCompilationUnit(ASTNode):
    """
    The ASTNestMLCompilationUnit class as used to store a collection of processed ASTNeurons.
    Grammar:
        nestMLCompilationUnit: (neuron | NEWLINE )* EOF;
    Attributes:
        neuron_list = None # a list of all processed neurons
        artifact_name = None
    """

    def __init__(self, neuron_list=None, artifact_name=None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param neuron_list: list of contained neurons
        :type neuron_list: List[ASTNeuron]
        :param artifact_name: the name of the file where ths model is contained in
        :type artifact_name: str
        """
        super(ASTNestMLCompilationUnit, self).__init__(*args, **kwargs)
        assert (artifact_name is not None and isinstance(artifact_name, str)), \
            '(PyNestML.AST.NestMLCompilationUnit) No or wrong type of artifact name provided (%s)!' % type(artifact_name)
        self.neuron_list = []
        if neuron_list is not None:
            assert type(neuron_list) is list
            self.neuron_list.extend(neuron_list)
        self.artifact_name = artifact_name

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTNestMLCompilationUnit
        """
        neuron_list_dup = [neuron.clone() for neuron in self.neuron_list]
        dup = ASTNestMLCompilationUnit(artifact_name=self.artifact_name,
                                       neuron_list=neuron_list_dup,
                                       # ASTNode common attributes:
                                       source_position=self.source_position,
                                       scope=self.scope,
                                       comment=self.comment,
                                       pre_comments=[s for s in self.pre_comments],
                                       in_comment=self.in_comment,
                                       post_comments=[s for s in self.post_comments],
                                       implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def add_neuron(self, neuron):
        """
        Expects an instance of neuron element which is added to the collection.
        :param neuron: an instance of a neuron
        :type neuron: ASTNeuron
        """
        assert (neuron is not None and isinstance(neuron, ASTNeuron)), \
            '(PyNestML.AST.CompilationUnit) No or wrong type of neuron provided (%s)!' % type(neuron)
        self.neuron_list.append(neuron)

    def delete_neuron(self, neuron):
        """
        Expects an instance of neuron element which is deleted from the collection.
        :param neuron: an instance of a ASTNeuron
        :type neuron:ASTNeuron
        :return: True if element deleted from list, False else.
        :rtype: bool
        """
        if self.neuron_list.__contains__(neuron):
            self.neuron_list.remove(neuron)
            return True
        return False

    def get_neuron_list(self):
        """
        :return: a list of neuron elements as stored in the unit
        :rtype: list(ASTNeuron)
        """
        return self.neuron_list

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for neuron in self.get_neuron_list():
            if neuron is ast:
                return self
            if neuron.get_parent(ast) is not None:
                return neuron.get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTNestMLCompilationUnit):
            return False
        if len(self.get_neuron_list()) != len(other.get_neuron_list()):
            return False
        my_neurons = self.get_neuron_list()
        your_neurons = other.get_neuron_list()
        for i in range(0, len(my_neurons)):
            if not my_neurons[i].equals(your_neurons[i]):
                return False
        return True

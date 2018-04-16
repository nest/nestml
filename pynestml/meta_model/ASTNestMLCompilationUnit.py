#
# ASTNestMLCompilationUnit.py
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


from pynestml.meta_model.ASTNeuron import ASTNeuron
from pynestml.meta_model.ASTNode import ASTNode


class ASTNestMLCompilationUnit(ASTNode):
    """
    The ASTNestMLCompilationUnit class as used to store a collection of processed ASTNeurons.
    """
    # a list of all processed neurons
    __neuronList = None
    __artifactName = None

    def __init__(self, source_position=None, artifact_name=None):
        """
        Standard constructor of ASTNestMLCompilationUnit.
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        :param artifact_name: the name of the file where ths model is contained in
        :type artifact_name: str
        """
        assert (artifact_name is not None and isinstance(artifact_name, str)), \
            '(PyNestML.AST.NestMLCompilationUnit) No or wrong type of artifact name provided (%s)!' % type(
                artifact_name)
        super(ASTNestMLCompilationUnit, self).__init__(source_position)
        self.__neuronList = list()
        self.__artifactName = artifact_name
        return

    def add_neuron(self, _neuron):
        """
        Expects an instance of neuron element which is added to the collection.
        :param _neuron: an instance of a neuron 
        :type _neuron: ASTNeuron
        :return: no returned value
        :rtype: void
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.AST.CompilationUnit) No or wrong type of neuron provided (%s)!' % type(_neuron)
        self.__neuronList.append(_neuron)
        return

    def delete_neuron(self, _neuron=None):
        """
        Expects an instance of neuron element which is deleted from the collection.
        :param _neuron: an instance of a ASTNeuron
        :type _neuron:ASTNeuron
        :return: True if element deleted from list, False else.
        :rtype: bool
        """
        if self.__neuronList.__contains__(_neuron):
            self.__neuronList.remove(_neuron)
            return True
        else:
            return False

    def get_neuron_list(self):
        """
        :return: a list of neuron elements as stored in the unit
        :rtype: list(ASTNeuron)
        """
        return self.__neuronList

    def get_parent(self, ast=None):
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
            elif neuron.get_parent(ast) is not None:
                return neuron.get_parent(ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the compilation unit.
        :return: a string representation.
        :rtype: str
        """
        ret = ''
        if self.get_neuron_list() is not None:
            for neuron in self.get_neuron_list():
                ret += str(neuron) + '\n'
        return ret

    def equals(self, other=None):
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

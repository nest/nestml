#
# ASTInputType.py
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


from pynestml.modelprocessor.ASTNode import ASTNode


class ASTInputType(ASTNode):
    """
    This class is used to store the type of a buffer.
    ASTInputType represents the type of the input line e.g.: inhibitory or excitatory:
    @attribute inhibitory true iff the neuron is a inhibitory.
    @attribute excitatory true iff. the neuron is a excitatory.
    Grammar:
        inputType : ('inhibitory' | 'excitatory');
    """
    __isInhibitory = False
    __isExcitatory = False

    def __init__(self, _isInhibitory=False, _isExcitatory=False, _sourcePosition=None):
        """
        Standard constructor.
        :param _isInhibitory: is inhibitory buffer.
        :type _isInhibitory: bool
        :param _isExcitatory: is excitatory buffer.
        :type _isExcitatory: book
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_isInhibitory is None or isinstance(_isInhibitory, bool)), \
            '(PyNestML.AST.InputType) Wrong type of specifier provided (%s)!' % type(_isInhibitory)
        assert (_isExcitatory is None or isinstance(_isExcitatory, bool)), \
            '(PyNestML.AST.InputType) Wrong type of specifier provided (%s)!' % type(_isExcitatory)
        assert (_isExcitatory != _isInhibitory), \
            '(PyNestML.AST.InputType) Buffer specification not correct!'
        super(ASTInputType, self).__init__(_sourcePosition)
        self.__isExcitatory = _isExcitatory
        self.__isInhibitory = _isInhibitory
        return

    def isExcitatory(self):
        """
        Returns whether it is excitatory type.
        :return: True if excitatory, otherwise False.
        :rtype: bool
        """
        return self.__isExcitatory

    def isInhibitory(self):
        """
        Returns whether it is inhibitory type.
        :return: True if inhibitory , otherwise False.
        :rtype: bool
        """
        return self.__isInhibitory

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        return None

    def __str__(self):
        """
        Returns a string representation of the input type.
        :return: a string representation.
        :rtype: str
        """
        if self.isInhibitory():
            return 'inhibitory'
        else:
            return 'excitatory'

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTInputType):
            return False
        return self.isExcitatory() == _other.isExcitatory() and self.isInhibitory() == _other.isInhibitory()

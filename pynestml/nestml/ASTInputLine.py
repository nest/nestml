#
# ASTInputLine.py
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
from pynestml.nestml.ASTElement import ASTElement
from pynestml.nestml.ASTOutputBlock import SignalType
from pynestml.nestml.ASTDatatype import ASTDatatype
from pynestml.nestml.ASTInputType import ASTInputType


class ASTInputLine(ASTElement):
    """
    This class is used to store a declaration of an input line.
    ASTInputLine represents a single line form the input, e.g.:
      spikeBuffer   <- inhibitory excitatory spike

    @attribute sizeParameter Optional parameter representing  multisynapse neuron.
    @attribute sizeParameter Type of the inputchannel: e.g. inhibitory or excitatory (or both).
    @attribute spike true iff the neuron is a spike.
    @attribute current true iff. the neuron is a current.
    Grammar:
          inputLine :
            name=NAME
            ('[' sizeParameter=NAME ']')?
            (datatype)?
            '<-' inputType*
            (isCurrent = 'current' | isSpike = 'spike');
    """
    __name = None
    __sizeParameter = None
    __dataType = None
    __inputTypes = None
    __signalType = None

    def __init__(self, _name=None, _sizeParameter=None, _dataType=None, _inputTypes=list(), _signalType=None,
                 _sourcePosition=None):
        """
        Standard constructor.
        :param _name: the name of the buffer
        :type _name: str
        :param _sizeParameter: a parameter indicating the index in an array.
        :type _sizeParameter:  str
        :param _dataType: the data type of this buffer
        :type _dataType: ASTDataType
        :param _inputTypes: a list of input types specifying the buffer.
        :type _inputTypes: list(ASTInputType)
        :param _signalType: type of signal received, i.e., spikes or currents
        :type _signalType: SignalType
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.AST.InputLine) No or wrong type of name provided (%s)!' % type(_name)
        assert (_signalType is not None and isinstance(_signalType, SignalType)), \
            '(PyNestML.AST.InputLine) No or wrong type of input signal type provided (%s)!' % type(_signalType)
        assert (_inputTypes is not None and isinstance(_inputTypes, list)), \
            '(PyNestML.AST.InputLine) No or wrong type of input types provided (%s)!' % type(_inputTypes)
        for typ in _inputTypes:
            assert (typ is not None and isinstance(typ, ASTInputType)), \
                '(PyNestML.AST.InputLine) No or wrong type of input type provided (%s)!' % type(typ)
        assert (_sizeParameter is None or isinstance(_sizeParameter, str)), \
            '(PyNestML.AST.InputLine) Wrong type of index parameter provided (%s)!' % type(_sizeParameter)
        assert (_dataType is None or isinstance(_dataType, ASTDatatype)), \
            '(PyNestML.AST.InputLine) Wrong type of data-type provided (%s)!' % type(_dataType)
        super(ASTInputLine, self).__init__(_sourcePosition)
        self.__signalType = _signalType
        self.__inputTypes = _inputTypes
        self.__sizeParameter = _sizeParameter
        self.__name = _name
        self.__dataType = _dataType
        return

    @classmethod
    def makeASTInputLine(cls, _name=None, _sizeParameter=None, _dataType=None, _inputTypes=list(), _signalType=None,
                         _sourcePosition=None):
        """
        Factory method of the ASTInputLine class.
        :param _name: the name of the buffer
        :type _name: str
        :param _sizeParameter: a parameter indicating the index in an array.
        :type _sizeParameter:  str
        :param _dataType: the data type of this buffer
        :type _dataType: ASTDataType
        :param _inputTypes: a list of input types specifying the buffer.
        :type _inputTypes: list(ASTInputType)
        :param _signalType: type of signal received, i.e., spikes or currents
        :type _signalType: SignalType
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTInputLine object.
        :rtype: ASTInputLine
        """
        return cls(_name=_name, _sizeParameter=_sizeParameter, _dataType=_dataType, _inputTypes=_inputTypes,
                   _signalType=_signalType, _sourcePosition=_sourcePosition)

    def getName(self):
        """
        Returns the name of the declared buffer.
        :return: the name.
        :rtype: str
        """
        return self.__name

    def hasIndexParameter(self):
        """
        Returns whether a index parameter has been defined.
        :return: True if index has been used, otherwise False.
        :rtype: bool
        """
        return self.__sizeParameter is not None

    def getIndexParameter(self):
        """
        Returns the index parameter.
        :return: the index parameter.
        :rtype: str
        """
        return self.__sizeParameter

    def hasInputTypes(self):
        """
        Returns whether input types have been defined.
        :return: True, if at least one input type has been defined.
        :rtype: bool
        """
        return len(self.__inputTypes) > 0

    def getInputTypes(self):
        """
        Returns the list of input types.
        :return: a list of input types.
        :rtype: list(ASTInputType)
        """
        return self.__inputTypes

    def isSpike(self):
        """
        Returns whether this is a spike buffer or not.
        :return: True if spike buffer, False else.
        :rtype: bool 
        """
        return self.__signalType is SignalType.SPIKE

    def isCurrent(self):
        """
        Returns whether this is a current buffer or not.
        :return: True if current buffer, False else.
        :rtype: bool 
        """
        return self.__signalType is SignalType.CURRENT

    def isExcitatory(self):
        """
        Returns whether this buffer is excitatory or not. For this, it has to be marked explicitly by the 
        excitatory keyword or no keywords at all shall occur (implicitly all types).
        :return: True if excitatory, False otherwise.
        :rtype: bool
        """
        if self.getInputTypes() is not None and len(self.getInputTypes()) == 0:
            return True
        for typE in self.getInputTypes():
            if typE.isExcitatory():
                return True
        return False

    def isInhibitory(self):
        """
        Returns whether this buffer is inhibitory or not. For this, it has to be marked explicitly by the 
        inhibitory keyword or no keywords at all shall occur (implicitly all types).
        :return: True if inhibitory, False otherwise.
        :rtype: bool
        """
        if self.getInputTypes() is not None and len(self.getInputTypes()) == 0:
            return True
        for typE in self.getInputTypes():
            if typE.isInhibitory():
                return True
        return False

    def hasDatatype(self):
        """
        Returns whether this buffer has a defined data type or not.
        :return: True if it has a datatype, otherwise False.
        :rtype: bool
        """
        return self.__dataType is not None and isinstance(self.__dataType, ASTDatatype)

    def getDatatype(self):
        """
        Returns the currently used data type of this buffer.
        :return: a single data type object.
        :rtype: ASTDatatype
        """
        return self.__dataType

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.hasDatatype():
            if self.getDatatype() is _ast:
                return self
            elif self.getDatatype().getParent(_ast) is not None:
                return self.getDatatype().getParent(_ast)
        for line in self.getInputTypes():
            if line is _ast:
                return self
            elif line.getParent(_ast) is not None:
                return line.getParent(_ast)
        return None

    def printAST(self):
        """
        Returns a string representation of the input line.
        :return: a string representing the input line.
        :rtype: str
        """
        ret = self.getName()
        if self.hasIndexParameter():
            ret += '[' + self.getIndexParameter() + ']'
        ret += '<-'
        if self.hasInputTypes():
            for iType in self.getInputTypes():
                ret += iType.printAST() + ' '
        if self.isSpike():
            ret += 'spike'
        else:
            ret += 'current'
        return ret

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal,otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTInputLine):
            return False
        if self.getName() != _other.getName():
            return False
        if self.hasIndexParameter() + _other.hasIndexParameter() == 1:
            return False
        if self.hasIndexParameter() and _other.hasIndexParameter() and \
                        self.getInputTypes() != _other.getIndexParameter():
            return False
        if self.hasDatatype() + _other.hasDatatype() == 1:
            return False
        if self.hasDatatype() and _other.hasDatatype() and not self.getDatatype().equals(_other.getDatatype()):
            return False
        if len(self.getInputTypes()) != len(_other.getInputTypes()):
            return False
        myInputTypes = self.getInputTypes()
        yourInputTypes = _other.getInputTypes()
        for i in range(0, len(myInputTypes)):
            if not myInputTypes[i].equals(yourInputTypes[i]):
                return False
        return self.isSpike() == _other.isSpike() and self.isCurrent() == _other.isCurrent()

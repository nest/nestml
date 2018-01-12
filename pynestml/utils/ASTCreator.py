#
# ASTCreator.py
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
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition


class ASTCreator(object):
    """
    This class contains a set of methods as used to create ASTs from strings.
    """

    @classmethod
    def createInternalBlock(cls, _neuron=None):
        """
        Creates a single internal block in the handed over neuron.
        :param _neuron: a single neuron
        :type _neuron: ASTNeuron
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
        if _neuron.getInternalsBlocks() is None:
            internal = ASTBlockWithVariables.makeASTBlockWithVariables(_isState=False, _isParameters=False,
                                                                       _isInternals=True, _isInitialValues=False,
                                                                       _declarations=list(), _sourcePosition=
                                                                       ASTSourcePosition.getAddedSourcePosition())
            _neuron.getBody().getBodyElements().append(internal)
        return _neuron

    @classmethod
    def createStateBlock(cls, _neuron=None):
        """
        Creates a single internal block in the handed over neuron.
        :param _neuron: a single neuron
        :type _neuron: ASTNeuron
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
        if _neuron.getInternalsBlocks() is None:
            state = ASTBlockWithVariables.makeASTBlockWithVariables(_isState=True, _isParameters=False,
                                                                    _isInternals=False, _isInitialValues=False,
                                                                    _declarations=list(), _sourcePosition=
                                                                    ASTSourcePosition.getAddedSourcePosition())
            _neuron.getBody().getBodyElements().append(state)
        return _neuron

    @classmethod
    def createInitialValuesBlock(cls, _neuron=None):
        """
        Creats a single initial values block in the handed over neuron.
        :param _neuron: a single neuron
        :type _neuron: ASTNeuron
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
        if _neuron.getInitialBlocks() is None:
            state = ASTBlockWithVariables.makeASTBlockWithVariables(_isState=False, _isParameters=False,
                                                                    _isInternals=False, _isInitialValues=True,
                                                                    _declarations=list(), _sourcePosition=
                                                                    ASTSourcePosition.getAddedSourcePosition())
            _neuron.getBody().getBodyElements().append(state)
        return _neuron

    @classmethod
    def createStatement(cls, _stmtAsString=None):
        """
        Creates a single statement from the given string.
        :param _stmtAsString: a statement as string
        :type _stmtAsString: str
        :return: a statement ast
        :rtype: ASTSmallStmt or ASTCompoundStmt
        """
        try:
            return ModelParser.parseStmt(_stmtAsString)
        except:
            raise RuntimeError('Cannot parse statement.')

    @classmethod
    def createDeclaration(cls, _declarationAsString=None):
        """
        Creates a single declaration from a given string.
        :param _declarationAsString: a declaration as string
        :type _declarationAsString: str
        :return: a single ast node
        :rtype: ASTDeclaration
        """
        try:
            return ModelParser.parseDeclaration(_declarationAsString)
        except:
            raise RuntimeError('Cannot parse declaration statement.')

    @classmethod
    def createShape(cls, _shapeAsString=None):
        """
        Creates a single shape from the given string.
        :param _shapeAsString: a shapes as a string
        :type _shapeAsString: str
        :return: a single shape ast
        :rtype: ASTOdeShape
        """
        try:
            return ModelParser.parseShape(_shapeAsString)
        except:
            raise RuntimeError('Cannot parse shape statement.')

    @classmethod
    def createAssignment(cls, _assignmentAsString=None):
        """
        Creats a single assignment from the given assignment.
        :param _assignmentAsString: a single assignment as a string.
        :type _assignmentAsString: str
        :return: a single assignment
        :rtype: ASTAssignment
        """
        try:
            return ModelParser.parseAssignment(_assignmentAsString)
        except:
            raise RuntimeError('Cannot parse assignment statement.')

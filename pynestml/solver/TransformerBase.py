#
# TransformerBase.py
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
from pynestml.nestml.NESTMLParser import NESTMLParser
from pynestml.nestml.ASTNeuron import ASTNeuron
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.OdeTransformer import OdeTransformer
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages
from pynestml.utils.ASTCreator import ASTCreator
from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter
import re as re


class TransformerBase(object):
    """
    This class contains several methods as used to adjust a given neuron instance to properties as
    returned by the solver.
    """

    @classmethod
    def addVariablesToInternals(cls, _neuron=None, _declarations=None):
        """
        Adds the variables as stored in the declaration tuples to the neuron.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :param _declarations: a list of declaration tuples
        :type _declarations: list((str,str))
        :return: a modified neuron
        :rtype: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.BaseTransformer) No or wrong type of neuron provided (%s)!' % type(_neuron)
        assert (_declarations is not None and isinstance(_declarations, list)), \
            '(PyNestML.Solver.BaseTransformer) No or wrong type of declarations provided (%s)!' % type(_declarations)
        for declaration in _declarations:
            cls.addVariableToInternals(_neuron, declaration)
        return _neuron

    @classmethod
    def addVariableToInternals(cls, _neuron=None, _declaration=None):
        """
        Adds the variable as stored in the declaration tuple to the neuron.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :param _declaration: a single declaration
        :type _declaration: dict
        :return: the neuron extended by the variable
        :rtype: ASTNeuron
        """
        try:
            (var, value) = ASTUtils.getTupleFromSingleDictEntry(_declaration)
            tmp = NESTMLParser.parseExpression(value)
            vectorVariable = ASTUtils.getVectorizedVariable(tmp, _neuron.getScope())
            declarationString = var + ' real' + (
                '[' + vectorVariable.getVectorParameter() + ']'
                if vectorVariable is not None and vectorVariable.hasVectorParameter() else '') + ' = ' + value
            astDeclaration = NESTMLParser.parseDeclaration(declarationString)
            if vectorVariable is not None:
                astDeclaration.setSizeParameter(vectorVariable.getVectorParameter())
            _neuron.addToInternalBlock(astDeclaration)
            return _neuron
        except:
            raise RuntimeError('Must not fail by construction.')

    @classmethod
    def replaceIntegrateCallThroughPropagation(cls, _neuron=None, _propagatorSteps=None):
        """
        Replaces all intergrate calls to the corresponding references to propagation.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :param _propagatorSteps: a list of propagator steps
        :type _propagatorSteps: list(str)
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        from pynestml.nestml.PredefinedFunctions import PredefinedFunctions
        from pynestml.nestml.ASTSmallStmt import ASTSmallStmt
        from pynestml.nestml.ASTBlock import ASTBlock
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.BaseTransformer) No or wrong type of neuron provided (%s)!' % type(_neuron)
        assert (_propagatorSteps is not None and isinstance(_propagatorSteps, list)), \
            '(PyNestML.Solver.BaseTransformer) No or wrong type of propagator steps provided (%s)!' % type(
                _propagatorSteps)
        integrateCall = ASTUtils.getFunctionCall(_neuron.getUpdateBlocks(), PredefinedFunctions.INTEGRATE_ODES)
        # by construction of a valid neuron, only a single integrate call should be there
        if isinstance(integrateCall, list):
            integrateCall = integrateCall[0]
        if integrateCall is not None:
            smallStatement = _neuron.getParent(integrateCall)
            assert (smallStatement is not None and isinstance(smallStatement, ASTSmallStmt))

            block = _neuron.getParent(smallStatement)
            assert (block is not None and isinstance(block, ASTBlock))
            for i in range(0, len(block.getStmts()) - 1):
                if block.getStmts()[i].equals(smallStatement):
                    del block.getStmts()[i]
                    block.getStmts()[i:i] = (ASTCreator.createStatement(st) for st in _propagatorSteps)
                    break
        else:
            code, message = Messages.getOdeSolutionNotUsed()
            Logger.logMessage(_neuron=_neuron, _code=code, _message=message, _errorPosition=_neuron.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.INFO)
        return _neuron

    @classmethod
    def addVariablesToInitialValues(cls, _neuron=None, _declarationsFile=None):
        """
        Adds a list with declarations to the internals block in the neuron.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :param _declarationsFile: a single
        :type _declarationsFile: list(tuple)
        :return: a modified neuron
        :rtype: ASTNeuron
        """
        for decl in _declarationsFile:
            cls.addVariableToInitialValue(_neuron, decl)
        return _neuron

    @classmethod
    def addVariableToInitialValue(cls, _neuron=None, _declaration=None):
        """
        Adds a single declaration to the internals block of the neuron.
        :param _neuron: a single neuron
        :type _neuron: ASTNeuron
        :param _declaration: a single key,value tuple
        :type _declaration: tuple
        :return: a modified neuron
        :rtype: ASTNeuron
        """
        try:
            (var, value) = _declaration
            tmp = NESTMLParser.parseExpression(value)
            vectorVariable = ASTUtils.getVectorizedVariable(tmp, _neuron.getScope())
            declarationString = var + ' real' + (
                '[' + vectorVariable.getVectorParameter() + ']'
                if vectorVariable is not None and vectorVariable.hasVectorParameter() else '') + ' = ' + \
                                value
            astDeclaration = NESTMLParser.parseDeclaration(declarationString)
            if vectorVariable is not None:
                astDeclaration.setSizeParameter(vectorVariable.getVectorParameter())
            _neuron.addToInitialValuesBlock(astDeclaration)
            return _neuron
        except:
            raise RuntimeError('Must not fail by construction.')

    @classmethod
    def applyIncomingSpikes(cls, _neuron=None):
        """
        Adds a set of update instructions to the handed over neuron.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.BaseTransformer) No or wrong type of neuron provided (%s)!' % type(_neuron)
        convCalls = OdeTransformer.get_sumFunctionCalls(_neuron)
        printer = ExpressionsPrettyPrinter()
        spikesUpdates = list()
        for convCall in convCalls:
            shape = convCall.getArgs()[0].getVariable().getCompleteName()
            buffer = convCall.getArgs()[1].getVariable().getCompleteName()
            initialValues = (_neuron.getInitialBlocks().getDeclarations()
                             if _neuron.getInitialBlocks() is not None else list())
            for astDeclaration in initialValues:
                for variable in astDeclaration.getVariables():

                    if re.match(shape + "[\']*", variable.getCompleteName()) or re.match(shape + '__[\\d]+$',
                                                                                        variable.getCompleteName()):
                        spikesUpdates.append(ASTCreator.createAssignment(
                            variable.getCompleteName() + " += " + buffer + " * " + printer.printExpression(
                                astDeclaration.getExpression())))
        for update in spikesUpdates:
            cls.addAssignmentToUpdateBlock(update, _neuron)
        return _neuron

    @classmethod
    def addAssignmentToUpdateBlock(cls, _assignment=None, _neuron=None):
        """
        Adds a single assignment to the end of the update block of the handed over neuron.
        :param _assignment: a single assignment
        :type _assignment: ASTAssignment
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        from pynestml.nestml.ASTSmallStmt import ASTSmallStmt
        from pynestml.nestml.ASTAssignment import ASTAssignment
        from pynestml.nestml.ASTSourcePosition import ASTSourcePosition
        assert (_assignment is not None and isinstance(_assignment, ASTAssignment)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of assignment provided (%s)!' % type(_assignment)
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of neuron provided (%s)!' % type(_neuron)
        smallStmt = ASTSmallStmt(_assignment=_assignment,_sourcePosition=ASTSourcePosition.getAddedSourcePosition())
        _neuron.getUpdateBlocks().getBlock().getStmts().append(smallStmt)
        return _neuron

    @classmethod
    def addDeclarationToUpdateBlock(cls, _declaration=None, _neuron=None):
        """
        Adds a single declaration to the end of the update block of the handed over neuron.
        :param _declaration:
        :type _declaration: ASTDeclaration
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :return: a modified neuron
        :rtype: ASTNeuron
        """
        from pynestml.nestml.ASTSmallStmt import ASTSmallStmt
        from pynestml.nestml.ASTDeclaration import ASTDeclaration
        assert (_declaration is not None and isinstance(_declaration, ASTDeclaration)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of declaration provided (%s)!' % type(_declaration)
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of neuron provided (%s)!' % type(_neuron)
        smallStmt = ASTSmallStmt(_declaration=_declaration,_sourcePosition=ASTSourcePosition.getAddedSourcePosition())
        _neuron.getUpdateBlocks().getBlock().getStmts().append(smallStmt)
        return _neuron

    @classmethod
    def computeShapeStateVariablesWithInitialValues(cls, _solverOutput=None):
        """
        Computes a set of state variables with the corresponding set of initial values from the given sovler output.
        :param _solverOutput: a single solver output file
        :type _solverOutput: SolverOutput
        :return: a list of variable initial value tuple as strings
        :rtype: tuple
        """
        from pynestml.solver.SolverOutput import SolverOutput
        assert (_solverOutput is not None and isinstance(_solverOutput, SolverOutput)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of solver output provided (%s)!' % tuple(_solverOutput)
        stateShapeVariablesWithInitialValues = list()
        for shapeStateVariable in _solverOutput.shape_state_variables:
            for initialValueAsDict in _solverOutput.initial_values:
                for var in initialValueAsDict.keys():
                    if var.endswith(shapeStateVariable):
                        stateShapeVariablesWithInitialValues.append((shapeStateVariable, initialValueAsDict[var]))
        return stateShapeVariablesWithInitialValues

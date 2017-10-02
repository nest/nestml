#
# CoCosTest.py
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

from __future__ import print_function

import unittest
import os
from pynestml.nestml.NESTMLParser import NESTMLParser
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.nestml.SymbolTable import SymbolTable
from pynestml.nestml.ASTSourcePosition import ASTSourcePosition
from pynestml.nestml.PredefinedTypes import PredefinedTypes
from pynestml.nestml.PredefinedFunctions import PredefinedFunctions
from pynestml.nestml.PredefinedUnits import PredefinedUnits
from pynestml.nestml.PredefinedVariables import PredefinedVariables
from pynestml.nestml.CoCosManager import CoCosManager

# minor setup steps required
Logger.initLogger(LOGGING_LEVEL.INFO)
SymbolTable.initializeSymbolTable(ASTSourcePosition(_startLine=0, _startColumn=0, _endLine=0, _endColumn=0))
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedVariables.registerPredefinedVariables()
PredefinedFunctions.registerPredefinedFunctions()
CoCosManager.initializeCoCosManager()


class ElementDefinedAfterUsage(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoVariableDefinedAfterUsage.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 2)


class ElementInSameLine(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoElementInSameLine.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 1)


class ElementNotDefinedInScope(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoVariableNotDefined.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 3)


class VariableRedeclaration(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoVariableRedeclared.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 2)


class EachBlockUnique(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoEachBlockUnique.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 2)


class FunctionUniqueAndDefined(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoFunctionNotUnique.nestml'))


class FunctionsHaveRhs(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoFunctionHasNoRhs.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 1)


class FunctionHasSeveralLhs(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoFunctionWithSeveralLhs.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 1)


class NoValuesAssignedToBuffers(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoValueAssignedToBuffer.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 2)


class OrderOfEquationsCorrect(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoNoOrderOfEquations.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 1)


class NumeratorOfUnitOne(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoUnitNumeratorNotOne.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 2)


class NamesOfNeuronsUnique(unittest.TestCase):
    def test(self):
        Logger.initLogger(LOGGING_LEVEL.NO)
        NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoMultipleNeuronsWithEqualName.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(None, LOGGING_LEVEL.ERROR)) == 1)


class NoNestCollision(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoNestNamespaceCollision.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 1)


class RedundantBufferKeywordsDetected(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoBufferWithRedundantTypes.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 1)


class ParametersAssignedOnlyInParametersBlock(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoParameterAssignedOutsideBlock.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 1)


class CurrentBuffersNotSpecifiedWithKeywords(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoCurrentBufferTypeSpecified.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 1)


class SpikeBufferWithoutDatatype(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoSpikeBufferWithoutType.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 1)


class FunctionWithWrongArgNumberDetected(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoFunctionCallNotConsistentWrongArgNumber.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 5)


class InitValuesHaveRhsAndOde(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoInitValuesWithoutOde.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 3)


class IncorrectReturnStmtDetected(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoIncorrectReturnStatement.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 4)


class OdeVarsOutsideInitBlockDetected(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoOdeVarNotInInitialValues.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 1)


class ConvolveCorrectlyDefined(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoConvolveNotCorrectlyProvided.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 3)


class VectorInNonVectorDeclarationDetected(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoVectorInNonVectorDeclaration.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 1)


class SumCorrectlyParametrized(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoSumNotCorrectlyParametrized.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 2)


class InvariantCorrectlyTyped(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoInvariantNotBool.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 1)


class ExpressionCorrectlyTyped(unittest.TestCase):
    def test(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'CoCoIllegalExpression.nestml'))
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 6)


if __name__ == '__main__':
    unittest.main()

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
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.CoCosManager import CoCosManager

# minor setup steps required
Logger.init_logger(LoggingLevel.INFO)
SymbolTable.initializeSymbolTable(ASTSourcePosition(_startLine=0, _startColumn=0, _endLine=0, _endColumn=0))
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedVariables.registerPredefinedVariables()
PredefinedFunctions.registerPredefinedFunctions()


class InvalidElementDefinedAfterUsage(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoVariableDefinedAfterUsage.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 2)


class ValidElementDefinedAfterUsage(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoVariableDefinedAfterUsage.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidElementInSameLine(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoElementInSameLine.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 1)


class ValidElementInSameLine(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoElementInSameLine.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidElementNotDefinedInScope(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoVariableNotDefined.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 3)


class ValidElementNotDefinedInScope(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoVariableNotDefined.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidVariableRedeclaration(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoVariableRedeclared.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 2)


class ValidVariableRedeclaration(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoVariableRedeclared.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidEachBlockUnique(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoEachBlockUnique.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 2)


class ValidEachBlockUnique(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoEachBlockUnique.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidFunctionUniqueAndDefined(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoFunctionNotUnique.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 4)


class ValidFunctionUniqueAndDefined(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoFunctionNotUnique.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidFunctionsHaveRhs(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoFunctionHasNoRhs.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 1)


class ValidFunctionsHaveRhs(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoFunctionHasNoRhs.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidFunctionHasSeveralLhs(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoFunctionWithSeveralLhs.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 1)


class ValidFunctionHasSeveralLhs(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoFunctionWithSeveralLhs.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidNoValuesAssignedToBuffers(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoValueAssignedToBuffer.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 2)


class ValidNoValuesAssignedToBuffers(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoValueAssignedToBuffer.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidOrderOfEquationsCorrect(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoNoOrderOfEquations.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 1)


class ValidOrderOfEquationsCorrect(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoNoOrderOfEquations.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidNumeratorOfUnitOne(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoUnitNumeratorNotOne.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 2)


class ValidNumeratorOfUnitOne(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoUnitNumeratorNotOne.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidNamesOfNeuronsUnique(unittest.TestCase):
    def test(self):
        Logger.init_logger(LoggingLevel.NO)
        ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoMultipleNeuronsWithEqualName.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(None, LoggingLevel.ERROR)) == 1)


class ValidNamesOfNeuronsUnique(unittest.TestCase):
    def test(self):
        Logger.init_logger(LoggingLevel.NO)
        ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoMultipleNeuronsWithEqualName.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(None, LoggingLevel.ERROR)) == 0)


class InvalidNoNestCollision(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoNestNamespaceCollision.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 1)


class ValidNoNestCollision(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoNestNamespaceCollision.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidRedundantBufferKeywordsDetected(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoBufferWithRedundantTypes.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 1)


class ValidRedundantBufferKeywordsDetected(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoBufferWithRedundantTypes.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidParametersAssignedOnlyInParametersBlock(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoParameterAssignedOutsideBlock.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 1)


class ValidParametersAssignedOnlyInParametersBlock(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoParameterAssignedOutsideBlock.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidCurrentBuffersNotSpecifiedWithKeywords(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoCurrentBufferTypeSpecified.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 1)


class ValidCurrentBuffersNotSpecifiedWithKeywords(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoCurrentBufferTypeSpecified.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidSpikeBufferWithoutDatatype(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoSpikeBufferWithoutType.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 1)


class ValidSpikeBufferWithoutDatatype(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoSpikeBufferWithoutType.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidFunctionWithWrongArgNumberDetected(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoFunctionCallNotConsistentWrongArgNumber.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 1)


class ValidFunctionWithWrongArgNumberDetected(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoFunctionCallNotConsistentWrongArgNumber.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidInitValuesHaveRhsAndOde(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoInitValuesWithoutOde.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 3)


class ValidInitValuesHaveRhsAndOde(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoInitValuesWithoutOde.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidIncorrectReturnStmtDetected(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoIncorrectReturnStatement.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 4)


class ValidIncorrectReturnStmtDetected(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoIncorrectReturnStatement.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidOdeVarsOutsideInitBlockDetected(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoOdeVarNotInInitialValues.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 1)


class ValidOdeVarsOutsideInitBlockDetected(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoOdeVarNotInInitialValues.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidConvolveCorrectlyDefined(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoConvolveNotCorrectlyProvided.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 3)


class ValidConvolveCorrectlyDefined(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoConvolveNotCorrectlyProvided.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidVectorInNonVectorDeclarationDetected(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoVectorInNonVectorDeclaration.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 1)


class ValidVectorInNonVectorDeclarationDetected(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoVectorInNonVectorDeclaration.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidSumCorrectlyParametrized(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoSumNotCorrectlyParametrized.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 2)


class ValidSumCorrectlyParametrized(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoSumNotCorrectlyParametrized.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidInvariantCorrectlyTyped(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoInvariantNotBool.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 1)


class ValidInvariantCorrectlyTyped(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoInvariantNotBool.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


class InvalidExpressionCorrectlyTyped(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoIllegalExpression.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 6)


class ValidExpressionCorrectlyTyped(unittest.TestCase):
    def test(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoIllegalExpression.nestml'))
        assert (len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0], LoggingLevel.ERROR)) == 0)


if __name__ == '__main__':
    unittest.main()

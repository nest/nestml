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
import re as re

from pynestml.meta_model.ASTNeuron import ASTNeuron
from pynestml.meta_model.ASTNodeFactory import ASTNodeFactory
from pynestml.meta_model.ASTSourceLocation import ASTSourceLocation
from pynestml.meta_model.ASTStmt import ASTStmt
from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.Messages import Messages
from pynestml.utils.ModelParser import ModelParser
from pynestml.utils.OdeTransformer import OdeTransformer


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
        (var, value) = ASTUtils.get_tuple_from_single_dict_entry(_declaration)
        tmp = ModelParser.parse_expression(value)
        vector_variable = ASTUtils.get_vectorized_variable(tmp, _neuron.get_scope())
        declaration_string = var + ' real' + (
            '[' + vector_variable.get_vector_parameter() + ']'
            if vector_variable is not None and vector_variable.has_vector_parameter() else '') + ' = ' + value
        ast_declaration = ModelParser.parse_declaration(declaration_string)
        if vector_variable is not None:
            ast_declaration.set_size_parameter(vector_variable.get_vector_parameter())
        _neuron.addToInternalBlock(ast_declaration)
        return _neuron

    @classmethod
    def replaceIntegrateCallThroughPropagation(cls, _neuron=None, _constInput=None, _propagatorSteps=None):
        """
        Replaces all intergrate calls to the corresponding references to propagation.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :param _constInput: an initial constant value
        :type _constInput: tuple
        :param _propagatorSteps: a list of propagator steps
        :type _propagatorSteps: list(str)
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        from pynestml.symbols.PredefinedFunctions import PredefinedFunctions
        from pynestml.meta_model.ASTSmallStmt import ASTSmallStmt
        from pynestml.meta_model.ASTBlock import ASTBlock
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.BaseTransformer) No or wrong type of neuron provided (%s)!' % type(_neuron)
        assert (_propagatorSteps is not None and isinstance(_propagatorSteps, list)), \
            '(PyNestML.Solver.BaseTransformer) No or wrong type of propagator steps provided (%s)!' % type(
                _propagatorSteps)
        integrate_call = ASTUtils.get_function_call(_neuron.get_update_blocks(), PredefinedFunctions.INTEGRATE_ODES)
        # by construction of a valid neuron, only a single integrate call should be there
        if isinstance(integrate_call, list):
            integrate_call = integrate_call[0]
        if integrate_call is not None:
            small_statement = _neuron.get_parent(integrate_call)
            assert (small_statement is not None and isinstance(small_statement, ASTSmallStmt))
            stmt = _neuron.get_parent(small_statement)
            assert (stmt is not None and isinstance(stmt, ASTStmt))
            block = _neuron.get_parent(_neuron.get_parent(small_statement))
            assert (block is not None and isinstance(block, ASTBlock))
            for i in range(0, len(block.get_stmts())):
                if block.get_stmts()[i].equals(stmt):
                    del block.get_stmts()[i]
                    const_tuple = ASTUtils.get_tuple_from_single_dict_entry(_constInput)
                    update_statements = list()
                    update_statements.append(ModelParser.parse_stmt(const_tuple[0] + " real = " + const_tuple[1]))
                    update_statements += list((ModelParser.parse_stmt(prop) for prop in _propagatorSteps))
                    block.get_stmts()[i:i] = update_statements
                    break
        else:
            code, message = Messages.getOdeSolutionNotUsed()
            Logger.log_message(neuron=_neuron, code=code, message=message,
                               error_position=_neuron.get_source_position(),
                               log_level=LoggingLevel.INFO)
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
            tmp = ModelParser.parse_expression(value)
            vector_variable = ASTUtils.get_vectorized_variable(tmp, _neuron.get_scope())
            declaration_string = var + ' real' + (
                '[' + vector_variable.get_vector_parameter() + ']'
                if vector_variable is not None and vector_variable.has_vector_parameter() else '') + ' = ' + value
            ast_declaration = ModelParser.parse_declaration(declaration_string)
            if vector_variable is not None:
                ast_declaration.set_size_parameter(vector_variable.get_vector_parameter())
            _neuron.addToInitialValuesBlock(ast_declaration)
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
        conv_calls = OdeTransformer.get_sum_function_calls(_neuron)
        printer = ExpressionsPrettyPrinter()
        spikes_updates = list()
        for convCall in conv_calls:
            shape = convCall.get_args()[0].get_variable().get_complete_name()
            buffer = convCall.get_args()[1].get_variable().get_complete_name()
            initialValues = (_neuron.get_initial_blocks().get_declarations()
            if _neuron.get_initial_blocks() is not None else list())
            for astDeclaration in initialValues:
                for variable in astDeclaration.get_variables():
                    if re.match(shape + "[\']*", variable.get_complete_name()) or re.match(shape + '__[\\d]+$',
                                                                                           variable.get_complete_name()):
                        assignment = ModelParser.parse_assignment(
                            variable.get_complete_name() + " += " + buffer + " * " + printer.printExpression(
                                astDeclaration.get_expression()))
                        spikes_updates.append(assignment)
        for update in spikes_updates:
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
        from pynestml.meta_model.ASTNodeFactory import ASTNodeFactory
        from pynestml.meta_model.ASTAssignment import ASTAssignment
        from pynestml.meta_model.ASTSourceLocation import ASTSourceLocation
        assert (_assignment is not None and isinstance(_assignment, ASTAssignment)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of assignment provided (%s)!' % type(_assignment)
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of neuron provided (%s)!' % type(_neuron)
        small_stmt = ASTNodeFactory.create_ast_small_stmt(assignment=_assignment,
                                                          source_position=ASTSourceLocation.get_added_source_position())
        stmt = ASTNodeFactory.create_ast_stmt(small_stmt=small_stmt,
                                              source_position=ASTSourceLocation.get_added_source_position())
        _neuron.get_update_blocks().get_block().get_stmts().append(stmt)
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
        from pynestml.meta_model.ASTDeclaration import ASTDeclaration
        assert (_declaration is not None and isinstance(_declaration, ASTDeclaration)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of declaration provided (%s)!' % type(_declaration)
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of neuron provided (%s)!' % type(_neuron)
        small_stmt = ASTNodeFactory.create_ast_small_stmt(declaration=_declaration,
                                                          source_position=ASTSourceLocation.get_added_source_position())
        stmt = ASTNodeFactory.create_ast_stmt(small_stmt=small_stmt,
                                              source_position=ASTSourceLocation.get_added_source_position())
        _neuron.get_update_blocks().get_block().get_stmts().append(stmt)
        return _neuron

    @classmethod
    def computeShapeStateVariablesWithInitialValues(cls, _solverOutput=None):
        """
        Computes a set of state variables with the corresponding set of initial values from the given solver output.
        :param _solverOutput: a single solver output file
        :type _solverOutput: SolverOutput
        :return: a list of variable initial value tuple as strings
        :rtype: tuple
        """
        from pynestml.solver.SolverOutput import SolverOutput
        assert (_solverOutput is not None and isinstance(_solverOutput, SolverOutput)), \
            '(PyNestML.Solver.TransformerBase) No or wrong type of solver output provided (%s)!' % tuple(_solverOutput)
        state_shape_variables_with_initial_values = list()
        for shapeStateVariable in _solverOutput.shape_state_variables:
            for initialValueAsDict in _solverOutput.initial_values:
                for var in initialValueAsDict.keys():
                    if var.endswith(shapeStateVariable):
                        state_shape_variables_with_initial_values.append((shapeStateVariable, initialValueAsDict[var]))
        return state_shape_variables_with_initial_values

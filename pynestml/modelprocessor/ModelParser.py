#
# ModelParser.py
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
from antlr4 import *

from pynestml.generated.PyNESTMLLexer import PyNESTMLLexer
from pynestml.generated.PyNESTMLParser import PyNESTMLParser
from pynestml.modelprocessor import ASTSymbolTableVisitor
from pynestml.modelprocessor.ASTBuilderVisitor import ASTBuilderVisitor
from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class ModelParser(object):
    """
    This class contains several method used to parse handed over models and returns them as one or more AST trees.
    """

    @classmethod
    def parseModel(cls, file_path=None):
        """
        Parses a handed over model and returns the ast representation of it.
        :param file_path: the path to the file which shall be parsed.
        :type file_path: str
        :return: a new ASTNESTMLCompilationUnit object.
        :rtype: ASTNESTMLCompilationUnit
        """
        try:
            inputFile = FileStream(file_path)
        except IOError:
            print('(PyNestML.Parser) File ' + str(file_path) + ' not found. Processing is stopped!')
            return
        code, message = Messages.getStartProcessingFile(file_path)
        Logger.logMessage(_neuron=None, _code=code, _message=message, _errorPosition=None, _logLevel=LOGGING_LEVEL.INFO)
        # create a lexer and hand over the input
        lexer = PyNESTMLLexer(inputFile)
        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()
        # parse the file
        parser = PyNESTMLParser(stream)
        compilationUnit = parser.nestmlCompilationUnit()
        # create a new visitor and return the new AST
        astBuilderVisitor = ASTBuilderVisitor(stream.tokens)
        ast = astBuilderVisitor.visit(compilationUnit)
        # create and update the corresponding symbol tables
        SymbolTable.initializeSymbolTable(ast.getSourcePosition())
        for neuron in ast.getNeuronList():
            ASTSymbolTableVisitor.ASTSymbolTableVisitor.updateSymbolTable(neuron)
            SymbolTable.addNeuronScope(neuron.getName(), neuron.getScope())

        # replace all derived variables through a computer processable names: e.g. g_in''' -> g_in__ddd
        restore_differential_order = []
        for ode in ASTUtils.getAll(ast, ASTOdeEquation):
            lhs_variable = ode.getLhs()
            if lhs_variable.getDifferentialOrder() > 0:
                lhs_variable.set_differential_order(lhs_variable.getDifferentialOrder() - 1)
                restore_differential_order.append(lhs_variable)

        for shape in ASTUtils.getAll(ast, ASTOdeShape):
            lhs_variable = shape.getVariable()
            if lhs_variable.getDifferentialOrder() > 0:
                lhs_variable.set_differential_order(lhs_variable.getDifferentialOrder() - 1)
                restore_differential_order.append(lhs_variable)

        # than replace remaining variables
        for variable in ASTUtils.getAll(ast, ASTVariable):

            if variable.getDifferentialOrder() > 0:
                variable.set_name(variable.getName() + "__" + "d" * variable.getDifferentialOrder())
                variable.set_differential_order(0)

        # now also equations have no ' at lhs. replace every occurrence of last d to ' to compensate
        for ode_variable in restore_differential_order:
            ode_variable.set_differential_order(1)

        #Logger.initLogger(Logger.get_current_logging_level())
        for neuron in ast.getNeuronList():
            ASTSymbolTableVisitor.ASTSymbolTableVisitor.updateSymbolTable(neuron)
            SymbolTable.addNeuronScope(neuron.getName(), neuron.getScope())
        return ast

    @classmethod
    def parseExpression(cls, _expression=None):
        """
        Parses a single expression and returns the corresponding ast.
        :param _expression: a single expression.
        :type _expression: str
        :return: a single expression
        :rtype: ASTExpression
        """
        assert (_expression is not None and (isinstance(_expression, str) or isinstance(_expression, unicode))), \
            '(PyNestML.Parser) No or wrong type of expression provided (%s)!' % type(_expression)
        # raw = 'neuron raw: state: ' + _expression + ' end end'
        lexer = PyNESTMLLexer(InputStream(_expression))
        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()
        # parse the file
        parser = PyNESTMLParser(stream)
        builder = ASTBuilderVisitor(stream.tokens)
        ret = builder.visit(parser.expression())
        ASTHigherOrderVisitor.visit(ret, lambda x: x.setSourcePosition(ASTSourcePosition.getAddedSourcePosition()))
        return ret

    @classmethod
    def parseDeclaration(cls, _declaration=None):
        """
        Parses a single declaration and returns the corresponding ast.
        :param _declaration: a single declaration.
        :type _declaration: str
        :return: a single declaration
        :rtype: ASTDeclaration
        """
        assert (_declaration is not None and (isinstance(_declaration, str) or isinstance(_declaration, unicode))), \
            '(PyNestML.Parser) No or wrong type of declaration provided (%s)!' % type(_declaration)
        lexer = PyNESTMLLexer(InputStream(_declaration))
        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()
        # parse the file
        parser = PyNESTMLParser(stream)
        builder = ASTBuilderVisitor(stream.tokens)
        ret = builder.visit(parser.declaration())
        ASTHigherOrderVisitor.visit(ret,lambda x: x.setSourcePosition(ASTSourcePosition.getAddedSourcePosition()))
        return ret

    @classmethod
    def parseStmt(cls, _statement=None):
        """
        Parses a single statement and returns the corresponding ast.
        :param _statement: a single statement
        :type _statement: str
        :return: a single statement object
        :rtype: ASTSmallStmt or ASTCompoundStmt
        """
        assert (_statement is not None and (isinstance(_statement, str) or isinstance(_statement, unicode))), \
            '(PyNestML.Parser) No or wrong type of statement provided (%s)!' % type(_statement)
        lexer = PyNESTMLLexer(InputStream(_statement))
        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()
        # parse the file
        parser = PyNESTMLParser(stream)
        builder = ASTBuilderVisitor(stream.tokens)
        ret = builder.visit(parser.stmt())
        ASTHigherOrderVisitor.visit(ret, lambda x: x.setSourcePosition(ASTSourcePosition.getAddedSourcePosition()))
        return ret

    @classmethod
    def parseShape(cls, _shape=None):
        """
        Parses a single shape and returns the corresponding ast.
        :param _shape: a single shape
        :type _shape: str
        :return: a single object
        :rtype: ASTOdeShape
        """
        assert (_shape is not None and (isinstance(_shape, str) or isinstance(_shape, unicode))), \
            '(PyNestML.Parser) No or wrong type of shape provided (%s)!' % type(_shape)
        lexer = PyNESTMLLexer(InputStream(_shape))
        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()
        # parse the file
        parser = PyNESTMLParser(stream)
        builder = ASTBuilderVisitor(stream.tokens)
        ret = builder.visit(parser.odeShape())
        ASTHigherOrderVisitor.visit(ret, lambda x: x.setSourcePosition(ASTSourcePosition.getAddedSourcePosition()))
        return ret

    @classmethod
    def parseAssignment(cls, _assignment=None):
        """
        Parses a single assignment and returns the corresponding ast.
        :param _assignment: a singe assignment as a string
        :type _assignment:  str
        :return: a single object.
        :rtype: ASTAssignment
        """
        assert (_assignment is not None and (isinstance(_assignment, str) or isinstance(_assignment, unicode))), \
            '(PyNestML.Parser) No or wrong type of assignment provided (%s)!' % type(_assignment)
        lexer = PyNESTMLLexer(InputStream(_assignment))
        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()
        # parse the file
        parser = PyNESTMLParser(stream)
        builder = ASTBuilderVisitor(stream.tokens)
        ret = builder.visit(parser.assignment())
        ASTHigherOrderVisitor.visit(ret, lambda x: x.setSourcePosition(ASTSourcePosition.getAddedSourcePosition()))
        return ret

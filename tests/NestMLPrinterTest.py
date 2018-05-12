import os
import unittest

from pynestml.meta_model.ASTSourceLocation import ASTSourceLocation
from pynestml.symbol_table.SymbolTable import SymbolTable
from pynestml.symbols.PredefinedFunctions import PredefinedFunctions
from pynestml.symbols.PredefinedTypes import PredefinedTypes
from pynestml.symbols.PredefinedUnits import PredefinedUnits
from pynestml.symbols.PredefinedVariables import PredefinedVariables
from pynestml.utils.ASTNestMLPrinter import ASTNestMLPrinter
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.ModelParser import ModelParser

# setups the infrastructure
PredefinedUnits.register_units()
PredefinedTypes.register_types()
PredefinedFunctions.register_functions()
PredefinedVariables.register_variables()
SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
Logger.init_logger(LoggingLevel.NO)


class NestMLPrinterTest(unittest.TestCase):
    """
    Tests if the NestML printer works as intended.
    TODO: work in progress
    """

    def test_complete_print(self):
        # model = ModelParser.parse_neuron(neuron)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')),
                         'NestMLPrinterTest.nestml'))
        # now create a new visitor and use it
        model_printer = ASTNestMLPrinter()
        #print(model_printer.print_node(model))
        # get the results and compare against constants
        return

    def test_block_with_variables_with_comments(self):
        block = '\n' \
                '/* pre1\n' \
                '* pre2\n' \
                '*/\n' \
                'state: # in\n' \
                'end\n' \
                '/* post1\n' \
                '* post2\n' \
                '*/\n\n'
        model = ModelParser.parse_block_with_variables(block)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(block, model_printer.print_node(model))

    def test_block_with_variables_without_comments(self):
        block = 'state:\n' \
                'end'
        model = ModelParser.parse_block_with_variables(block)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(block, model_printer.print_node(model))

    def test_assignment_with_comments(self):
        assignment = '\n' \
                     '/* pre */\n' \
                     'a = b # in\n' \
                     '/* post */\n' \
                     '\n'
        model = ModelParser.parse_assignment(assignment)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(assignment, model_printer.print_node(model))

    def test_assignment_without_comments(self):
        assignment = 'a = b\n'
        model = ModelParser.parse_assignment(assignment)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(assignment, model_printer.print_node(model))

    def test_function_call_with_comments(self):
        function_call = '\n/* pre */\n' \
                        'min(1,2) # in\n' \
                        '/* post */\n\n'
        model = ModelParser.parse_stmt(function_call)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(function_call, model_printer.print_node(model))

    def test_function_call_without_comments(self):
        function_call = 'min(1,2)\n'
        model = ModelParser.parse_stmt(function_call)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(function_call, model_printer.print_node(model))

    def test_neuron_with_comments(self):
        neuron = '\n/*pre*/\n' \
                 'neuron test: # in\n' \
                 'end\n' \
                 '/*post*/\n\n'
        model = ModelParser.parse_neuron(neuron)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(neuron, model_printer.print_node(model))

    def test_neuron_without_comments(self):
        neuron = 'neuron test:\n' \
                 'end\n'
        model = ModelParser.parse_neuron(neuron)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(neuron, model_printer.print_node(model))

    def test_declaration_with_comments(self):
        declaration = '\n' \
                      '/*pre*/\n' \
                      'test mV = 10mV # in\n' \
                      '/*post*/\n\n'
        model = ModelParser.parse_declaration(declaration)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(declaration, model_printer.print_node(model))

    def test_declaration_without_comments(self):
        declaration = 'test mV = 10mV'
        model = ModelParser.parse_declaration(declaration)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(declaration, model_printer.print_node(model))

    def test_equations_block_with_comments(self):
        block = '\n/*pre*/\n' \
                'equations: # in\n' \
                'end\n' \
                '/*post*/\n\n'
        model = ModelParser.parse_equations_block(block)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(block, model_printer.print_node(model))

    def test_equations_block_without_comments(self):
        block = 'equations:\n' \
                'end\n'
        model = ModelParser.parse_equations_block(block)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(block, model_printer.print_node(model))

    def test_for_stmt_with_comments(self):
        stmt = '\n/*pre*/\n' \
               'for i in 10 - 3.14...10 + 3.14 step -1: # in\n' \
               'end\n' \
               '/*post*/\n\n'
        model = ModelParser.parse_for_stmt(stmt)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(stmt, model_printer.print_node(model))

    def test_for_stmt_without_comments(self):
        stmt = 'for i in 10 - 3.14...10 + 3.14 step -1: # in\n' \
               'end\n'
        model = ModelParser.parse_for_stmt(stmt)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(stmt, model_printer.print_node(model))

    def test_while_stmt_with_comments(self):
        stmt = '\n/*pre*/\n' \
               'while true: # in \n' \
               'end\n' \
               '/*post*/\n\n'
        model = ModelParser.parse_while_stmt(stmt)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(stmt, model_printer.print_node(model))

    def test_while_stmt_without_comments(self):
        stmt = 'while true:\n' \
               'end\n'
        model = ModelParser.parse_while_stmt(stmt)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(stmt, model_printer.print_node(model))

    def test_update_block_with_comments(self):
        block = '\n/*pre*/\n' \
                'update: # in\n' \
                'end\n' \
                '/*post*/\n\n'
        model = ModelParser.parse_update_block(block)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(block, model_printer.print_node(model))

    def test_update_block_without_comments(self):
        block = 'update:\n' \
                'end\n'
        model = ModelParser.parse_update_block(block)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(block, model_printer.print_node(model))

    def test_variable(self):
        var = 'V_m'
        model = ModelParser.parse_variable(var)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(var, model_printer.print_node(model))

    def test_unit_type(self):
        unit = '1/(mV*kg**2)'
        model = ModelParser.parse_unit_type(unit)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(unit, model_printer.print_node(model))

    def test_unary_operator(self):
        ops = {'-', '+', '~'}
        for op in ops:
            model = ModelParser.parse_unary_operator(op)
            model_printer = ASTNestMLPrinter()
            self.assertEqual(op, model_printer.print_node(model))
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

    def test_neuron_print(self):
        neuron = \
            'neuron neuron_print_test:\n' \
            '   state:\n' \
            '       test_var mV = 10mV\n' \
            '   end\n' \
            'end\n' \
            ''
        # model = ModelParser.parse_neuron(neuron)
        model = ModelParser.parse_model(os.path.join(os.path.dirname(__file__),
                                                     os.path.join(os.path.join('..', 'models'),
                                                                  'aeif_cond_alpha.nestml')))
        # now create a new visitor and use it
        model_printer = ASTNestMLPrinter()
        #print(model_printer.print_node(model))
        # get the results and compare against constants
        return

    def test_block_with_variables_with_comments(self):
        block = '/* pre1\n' \
                '* pre2\n' \
                '*/\n' \
                'state: # in\n' \
                'end\n' \
                '/* post1\n' \
                '* post2\n' \
                '*/\n'
        model = ModelParser.parse_block_with_variables(block)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(model_printer.print_node(model), block)

    def test_block_with_variables_without_comments(self):
        block = 'state:\n' \
                'end'
        model = ModelParser.parse_block_with_variables(block)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(model_printer.print_node(model), block)

    def test_assignment_with_comments(self):
        assignment = '/* pre */\n' \
                     'a = b # in\n' \
                     '/* post */\n'
        model = ModelParser.parse_assignment(assignment)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(model_printer.print_node(model), assignment)

    def test_assignment_without_comments(self):
        assignment = 'a = b\n'
        model = ModelParser.parse_assignment(assignment)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(model_printer.print_node(model), assignment)

    def test_function_call_with_comments(self):
        function_call = '/* pre */\n' \
                        'min(1,2) # in\n' \
                        '/* post */\n'
        model = ModelParser.parse_stmt(function_call)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(model_printer.print_node(model), function_call)

    def test_function_call_without_comments(self):
        function_call = 'min(1,2)\n'
        model = ModelParser.parse_stmt(function_call)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(model_printer.print_node(model), function_call)

    def test_neuron_with_comments(self):
        neuron = '/*pre*/\n' \
                 'neuron test: # in\n' \
                 'end\n' \
                 '/*post*/\n'
        model = ModelParser.parse_neuron(neuron)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(model_printer.print_node(model), neuron)

    def test_neuron_without_comments(self):
        neuron = 'neuron test:\n' \
                 'end\n'
        model = ModelParser.parse_neuron(neuron)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(model_printer.print_node(model), neuron)

    def test_declaration_with_comments(self):
        declaration = '/*pre*/\n' \
                      'test mV = 10mV # in\n' \
                      '/*post*/\n'
        model = ModelParser.parse_declaration(declaration)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(model_printer.print_node(model), declaration)

    def test_declaration_without_comments(self):
        declaration = 'test mV = 10mV\n'
        model = ModelParser.parse_declaration(declaration)
        model_printer = ASTNestMLPrinter()
        self.assertEqual(model_printer.print_node(model), declaration)

import os
import unittest

from pynestml.meta_model.ASTSourceLocation import ASTSourceLocation
from pynestml.symbol_table.SymbolTable import SymbolTable
from pynestml.symbols.PredefinedFunctions import PredefinedFunctions
from pynestml.symbols.PredefinedTypes import PredefinedTypes
from pynestml.symbols.PredefinedUnits import PredefinedUnits
from pynestml.symbols.PredefinedVariables import PredefinedVariables
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.ModelParser import ModelParser
from pynestml.visitors.ASTNestMLPrinter import ASTNestMLPrinter

# setups the infrastructure
PredefinedUnits.register_units()
PredefinedTypes.register_types()
PredefinedFunctions.register_functions()
PredefinedVariables.register_variables()
SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
Logger.init_logger(LoggingLevel.NO)


class NESTMLTest(unittest.TestCase):
    """
    Tests if the overall model processing frontend works as intended.
    """

    def test_neuron_print(self):
        neuron = \
            'neuron neuron_print_test:\n' \
            '   state:\n' \
            '       test_var mV = 10mV\n' \
            '   end\n' \
            'end\n' \
            ''
        model = ModelParser.parse_neuron(neuron)
        # now create a new visitor and use it
        model_printer = ASTNestMLPrinter()
        print(model_printer.print_node(model))
        # get the results and compare against constants
        return

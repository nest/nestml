from pynestml.utils.mechs_info_enricher import MechsInfoEnricher
from pynestml.utils.model_parser import ModelParser
import sympy
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor

class ConcInfoEnricher(MechsInfoEnricher):

    def __init__(self, params):
        super(MechsInfoEnricher, self).__init__(params)

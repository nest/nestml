from pynestml.utils.mechs_info_enricher import MechsInfoEnricher
from pynestml.utils.model_parser import ModelParser
import sympy
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor

class ConcInfoEnricher(MechsInfoEnricher):
    """Just created for consistency. No more than the base-class enriching needs to be done"""
    def __init__(self, params):
        super(MechsInfoEnricher, self).__init__(params)

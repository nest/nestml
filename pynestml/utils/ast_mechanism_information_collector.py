from collections import defaultdict
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.visitors.ast_visitor import ASTVisitor

class ASTMechanismInformationCollector(object):

    collector_visitor = None
    neuron = None

    @classmethod
    def __init__(cls, neuron):
        cls.neuron = neuron
        cls.collector_visitor = ASTMechanismInformationCollectorVisitor()
        neuron.accept(cls.collector_visitor)

    @classmethod
    def detect_mechs(cls, mechType: str):
        mechs_info = defaultdict()
        if not FrontendConfiguration.target_is_compartmental():
            return mechs_info

        mechanism_expressions = cls.collector_visitor.get_mech_root_expressions(cls.neuron, mechType)
        for mechanism_expression in mechanism_expressions:
            mechanism_name = mechanism_expression.variable_name
            mechs_info[mechanism_name] = defaultdict()
            mechs_info[mechanism_name]["root_expression"] = mechanism_expression

        return mechs_info

class ASTMechanismInformationCollectorVisitor(ASTVisitor):

    @classmethod
    def get_mech_root_expression(cls, neuron, mechType: str):


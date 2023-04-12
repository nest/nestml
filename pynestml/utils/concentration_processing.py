from pynestml.utils.mechanism_processing import MechanismProcessing
from collections import defaultdict

from pynestml.meta_model.ast_neuron import ASTNeuron

class ConcentrationProcessing(MechanismProcessing):

    mechType = "concentration"

    def __init__(self, params):
        super(MechanismProcessing, self).__init__(params)

    @classmethod
    def collect_information_for_specific_mech_types(cls, neuron, mechs_info):
        for mechanism_name, mechanism_info in mechs_info.items():
            #Create fake mechs_info such that it can be processed by the existing ode_toolbox_processing function.
            fake_mechs_info = defaultdict()
            fake_mechanism_info = defaultdict()
            fake_mechanism_info["ODEs"] = list()
            fake_mechanism_info["ODEs"].append(mechanism_info["root_expression"])
            fake_mechs_info["fake"] = fake_mechanism_info

            fake_mechs_info = cls.ode_toolbox_processing(neuron, fake_mechs_info)

            mechs_info[mechanism_name]["ODEs"] = mechs_info[mechanism_name]["ODEs"] | fake_mechs_info["fake"]["ODEs"]

        return mechs_info
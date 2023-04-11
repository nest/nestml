from pynestml.utils.mechanism_processing import MechanismProcessing
from collections import defaultdict

from pynestml.meta_model.ast_neuron import ASTNeuron

class ConcentrationProcessing(MechanismProcessing):
    def __init__(self, params):
        super(MechanismProcessing, self).__init__(params)

    @classmethod
    def get_mechs_info(cls, neuron: ASTNeuron, mechType="concentration"):
        return MechanismProcessing.get_mechs_info(neuron, "concentration")

    @classmethod
    def check_co_co(cls, neuron: ASTNeuron, mechType="concentration"):
        return MechanismProcessing.check_co_co(neuron, "concentration")

    def collect_information_for_specific_mech_types(self, neuron, mechs_info):
        for mechanism_name, mechanism_info in mechs_info.items():
            #Create fake mechs_info such that it can be processed by the existing ode_toolbox_processing function.
            fake_mechs_info = defaultdict()
            fake_mechanism_info = defaultdict()
            fake_mechanism_info["ODEs"] = list(mechanism_info["root_expression"])
            fake_mechs_info["fake"] = fake_mechanism_info

            fake_mechs_info = self.ode_toolbox_processing(neuron, fake_mechs_info)

            mechs_info[mechanism_name]["ODEs"].append(fake_mechs_info["fake"]["ODEs"])

        return mechs_info
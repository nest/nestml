import copy

from pynestml.utils.mechanism_processing import MechanismProcessing

from collections import defaultdict

class ContinuousInputProcessing(MechanismProcessing):
    mechType = "continuous_input"

    def __init__(self, params):
        super(MechanismProcessing, self).__init__(params)

    @classmethod
    def collect_information_for_specific_mech_types(cls, neuron, mechs_info):
        for continuous_name, continuous_info in mechs_info.items():
            continuous = defaultdict()
            for port in continuous_info["Continuous"]:
                continuous[port.name] = copy.deepcopy(port)
            mechs_info[continuous_name]["Continuous"] = continuous

        return mechs_info

import os
import pytest

from pynestml.frontend.pynestml_frontend import generate_spinnaker2_target


class TestSpiNNaker2IzhikevichNeuron:
    """SpiNNaker2 code generation tests"""

    # @pytest.fixture(autouse=True,
    #                 scope="module")
    def generate_code(self):
        codegen_opts = {"quantity_to_preferred_prefix": {"electrical potential": "m",  # needed for V_m_init and U_m
                                                         "electrical current": "p",
                                                         "electrical resistance": "G",
                                                         "frequency":"k",
                                                         "time": "m",
                                                         "electrical capacitance": "p",
                                                         },
                        "solver":'numeric',
                        "numeric_solver": "forward-Euler"}
        files = [
            os.path.join("models", "neurons", "izhikevich_neuron_psc_exp_NO_ISTIM.nestml"),
        ]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir + os.sep + os.pardir, s))) for s in files]
        target_path = "spinnaker2-target"
        install_path = "spinnaker2-install"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = ''#"_nestml"
        generate_spinnaker2_target(input_path,
                                  target_path=target_path,
                                  install_path=install_path,
                                  logging_level=logging_level,
                                  module_name=module_name,
                                  suffix=suffix,
                                 codegen_opts=codegen_opts)

    def test_generate_code(self):
        self.generate_code()
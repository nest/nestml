import os
import pytest

from pynestml.frontend.pynestml_frontend import generate_spinnaker2_target


class TestSpiNNaker2IafPscExp:
    """SpiNNaker2 code generation tests"""

    # @pytest.fixture(autouse=True,
    #                 scope="module")
    def generate_code(self):
        # codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
        #                                           "synapse": "stdp_synapse",
        #                                           "post_ports": ["post_spikes"]}]}

        files = [
            os.path.join("models", "neurons", "iaf_psc_exp_neuron_NO_ISTIM.nestml"),
            # os.path.join("models", "synapses", "stdp_synapse.nestml")
        ]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
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
                                  suffix=suffix)
        #                          codegen_opts=codegen_opts)

    def test_generate_code(self):
        self.generate_code()
"""
wb_cond_exp_test.py
"""

import os
import nest
import unittest
import numpy as np 
from pynestml.frontend.pynestml_frontend import to_nest, install_nest

try:
    import matplotlib
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except:
    TEST_PLOTS = False



class NestWBCondExpTest(unittest.TestCase):
    
    def test_wb_cond_exp(self):

        if not os.path.exists("target"):
            os.makedirs("target")

        input_path = os.path.join(os.path.realpath(os.path.join(
        os.path.dirname(__file__), "resources", "wb_cond_exp.nestml")))
        target_path = "target"
        module_name = 'nestml_module'
        nest_path = "/home/abolfazl/prog/install-dir/nest-simulator-2.18.0_build"
        suffix = '_nestml'

        to_nest(input_path=input_path,
                target_path=target_path,
                logging_level="INFO",
                suffix=suffix,
                module_name=module_name)

        install_nest(target_path, nest_path)

        nest.Install("nestml_module")
        model = "wb_cond_exp_nestml"

        dt = 0.01
        t_simulation = 1000.0
        nest.SetKernelStatus({"resolution": dt})

        neuron = nest.Create(model)
        parameters = nest.GetDefaults(model)

        # if 0:
        #     for i in parameters:
        #         print(i, parameters[i])

        nest.SetStatus(neuron, {'I_e': 75.0})
        multimeter = nest.Create("multimeter")
        nest.SetStatus(multimeter, {"withtime": True,
                                    "record_from": ["V_m"],
                                    "interval": dt})
        spikedetector = nest.Create("spike_detector",
                                    params={"withgid": True,
                                            "withtime": True})
        nest.Connect(multimeter, neuron)
        nest.Connect(neuron, spikedetector)
        nest.Simulate(t_simulation)
        
        dmm = nest.GetStatus(multimeter)[0]
        Voltages = dmm["events"]["V_m"]
        tv = dmm["events"]["times"]
        dSD = nest.GetStatus(spikedetector, keys='events')[0]
        spikes = dSD['senders']
        ts = dSD["times"]

        firing_rate = len(spikes) / t_simulation * 1000
        print("firing rate is ", firing_rate)
        expected_value = np.abs(firing_rate - 50)
        tolerance_value = 5  # Hz 

        self.assertLessEqual(expected_value, tolerance_value)


        if TEST_PLOTS:

            fig, ax = plt.subplots(2, figsize=(8, 6), sharex=True)
            ax[0].plot(tv, Voltages, lw=2, color="k")
            ax[1].plot(ts, spikes, 'ko')
            ax[1].set_xlabel("Time [ms]")
            ax[1].set_xlim(0, t_simulation)
            ax[1].set_ylabel("Spikes")
            ax[0].set_ylabel("v [ms]")
            ax[0].set_ylim(-100, 50)

            for i in ts:
                ax[0].axvline(x=i, lw=1., ls="--", color="gray")

            plt.savefig("resources/wb_cond_exp.png")
            # plt.show()

if __name__ == "__main__":
    unittest.main()
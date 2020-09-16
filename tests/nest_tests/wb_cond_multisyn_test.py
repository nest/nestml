"""
wb_cond_multisyn_test.py
"""
try:
    import matplotlib as mpl
    mpl.use("Agg")
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


import os
import nest
import unittest
import numpy as np
from pynestml.frontend.pynestml_frontend import to_nest, install_nest


class NestWBCondExpTest(unittest.TestCase):

    def test_wb_cond_multisyn(self):

        if not os.path.exists("target"):
            os.makedirs("target")

        input_path = os.path.join(os.path.realpath(os.path.join(
            os.path.dirname(__file__), "../../models", "wb_cond_multisyn.nestml")))
        target_path = "target"
        module_name = 'nestmlmodule'
#        nest_path = "/home/travis/nest_install"
        nest_path = "/home/archels/nest-simulator-build"
        suffix = '_nestml'

        to_nest(input_path=input_path,
                target_path=target_path,
                logging_level="INFO",
                suffix=suffix,
                module_name=module_name)

        install_nest(target_path, nest_path)

        nest.Install("nestmlmodule")
        model = "wb_cond_multisyn_nestml"

        dt = 0.01
        t_simulation = 1000.0
        nest.SetKernelStatus({"resolution": dt})

        neuron = nest.Create(model)
        parameters = nest.GetDefaults(model)

        neuron.set({'I_e': 75.0})
        multimeter = nest.Create("multimeter")
        multimeter.set({"record_from": ["V_m"],
                        "interval": dt})
        spikedetector = nest.Create("spike_detector")
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

            plt.savefig("resources/wb_cond_multisyn.png")
            # plt.show()

        self.assertLessEqual(expected_value, tolerance_value)


if __name__ == "__main__":
    unittest.main()

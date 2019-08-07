#
# nest_integration_test_multisynapse.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

import nest

TEST_PLOTS = True
if TEST_PLOTS:
    import matplotlib
    import matplotlib.pyplot as plt

nest.set_verbosity("M_ALL")
nest.Install("nestmlmodule")


def test_multysinapse():
    neuron1 = nest.Create("iaf_psc_alpha_multisynapse_neuron")
    neuron2 = nest.Create("iaf_psc_alpha_multisynapse_neuron")

    nest.SetDefaults("iaf_psc_alpha_multisynapse", {"tau_syn": [1.0, 2.0]})

    spikegenerator = nest.Create('spike_generator', params={'spike_times': [100.0, 200.0]})

    syn_dict = {"model": "static_synapse", "weight": 2.5, 'receptor_type': 1}

    nest.Connect(spikegenerator, neuron2, syn_spec=syn_dict)
    nest.Connect(spikegenerator, neuron1, syn_spec=syn_dict)

    # nest.SetStatus(neuron1, {"I_e": 376.0})
    # nest.SetStatus(neuron2, {"I_e": 376.0})

    multimeter1 = nest.Create('multimeter')
    multimeter2 = nest.Create('multimeter')

    V_m_specifier = 'V_m'  # 'delta_V_m'
    nest.SetStatus(multimeter1, {"withtime": True, "record_from": [V_m_specifier]})
    nest.SetStatus(multimeter2, {"withtime": True, "record_from": [V_m_specifier]})

    nest.Connect(multimeter1, neuron1)
    nest.Connect(multimeter2, neuron2)

    nest.Simulate(400.0)
    dmm1 = nest.GetStatus(multimeter1)[0]
    Vms1 = dmm1["events"][V_m_specifier]
    ts1 = dmm1["events"]["times"]

    events1 = dmm1["events"]
    pylab.figure(1)

    dmm2 = nest.GetStatus(multimeter2)[0]
    Vms2 = dmm2["events"][V_m_specifier]
    ts2 = dmm2["events"]["times"]

    pylab.plot(ts1, Vms1)
    pylab.plot(ts2, Vms2)

    pylab.show()

    for index in range(0, len(Vms1)):
        if abs(Vms1[index] - Vms2[index]) > 0.000001:
            print('!!!!!!!!!!!!!!!!!!!!')
            print(str(Vms1[index]) + " divers from  " + str(Vms2[index]) + " at iteration: " + str(
                index) + " of overall iterations: " + str(len(Vms1)))
            print('!!!!!!!!!!!!!!!!!!!!')
            raise Exception("TEST FAILED")
        elif abs(Vms1[index] - Vms2[index]) > 0:
            print("Greater than 0 difference" + str(abs(Vms1[index] - Vms2[index])) + " at iteration: " + str(
                index) + " of overall iterations: " + str(len(Vms1)))
    print("Test: PASSED")


if __name__ == "__main__":
    # execute only if run as a script
    # test_multysinapse()

import nest

models = nest.Models(mtype="nodes")
neuron_models = [m for m in models if str(nest.GetDefaults(m, "element_type")) == "neuron"]
syn_models = nest.Models(mtype="synapses")

print("Before: had " + str(len(neuron_models)) + " neuron models")





#import os
#os.environ["NEST_PATH"] = "/home/archels/julich/nest-simulator-build"
#os.environ["LD_LIBRARY_PATH"] = "/home/archels/julich/nest-simulator-build/lib:/home/archels/julich/nest-simulator-build/lib/python3.6/site-packages/nest:/tmp/nestml-target"
#os.environ["SLI_PATH"] = "/tmp/nestml-target/sli"

from pynestml.frontend.pynestml_frontend import to_nest, install_nest

#to_nest(input_path="/home/archels/julich/nestml-fork/nestml/models/aeif_cond_alpha.nestml", target_path="/tmp/work_pynestml/target")
to_nest(input_path="/home/archels/julich/nestml-fork/nestml/models/iaf_psc_exp.nestml", target_path="/tmp/nestml-target", dev=True, suffix="_nestml")

install_nest("/tmp/nestml-target", "/home/archels/julich/nest-simulator-build")

nest.set_verbosity("M_ALL")
#nest.set_debug(True)

nest.Install("nestmlmodule")

#nest.Simulate(1.)





new_models = nest.Models(mtype="nodes")
new_neuron_models = [m for m in new_models if str(nest.GetDefaults(m, "element_type")) == "neuron"]
new_syn_models = nest.Models(mtype="synapses")

print("After: have " + str(len(new_neuron_models)) + " neuron models")

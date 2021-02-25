from pynestml.frontend.pynestml_frontend import to_nest, install_nest

to_nest(input_path="/home/name/thesis/eclipse/workspace/nestml/models/iaf_psc_exp.nestml", target_path="/home/name/eclipse-thesis/workspace/nestml/generated")

install_nest("/home/name/thesis/eclipse/workspace/nestml/generated", "/home/name/thesis/nest-simulator/build_master_nompi/install")

nest.Install("nestmlmodule")
nest.Create("cm_main")
# ...
#nest.Simulate(400.)
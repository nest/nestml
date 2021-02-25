import os

from pynestml.frontend.pynestml_frontend import to_nest, install_nest

# string = "python setup.py install --user"
# os.system(string)

# /home/name/thesis/eclipse/workspace/nestml
# sandbox.run_setup('setup.py', ['install', '--user'])


THESIS_HOME = "/home/name/thesis"

NESTML_HOME_SUFFIX = "/eclipse/workspace/nestml"
NESTSIM_INSTALL_SUFFIX = "/nest-simulator/build_master_nompi/install"

NESTML_HOME = THESIS_HOME + NESTML_HOME_SUFFIX
NESTSIM_HOME = THESIS_HOME + NESTSIM_INSTALL_SUFFIX


# to_nest(input_path=os.path.join(NESTML_HOME, "models/iaf_test.nestml"), 
        # target_path=os.path.join(NESTML_HOME, "generated"))

to_nest(input_path=os.path.join(NESTML_HOME, "models/iaf_psc_exp.nestml"), 
        target_path=os.path.join(NESTML_HOME, "generated"))

install_nest(os.path.join(NESTML_HOME, "generated"), NESTSIM_HOME)

nest.Install("nestmlmodule")
nest.Create("cm_main")
# ...
#nest.Simulate(400.)

#rmtree(os.path.join(NESTML_HOME, "generated"))














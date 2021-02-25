import os
from shutil import rmtree 

from pynestml.frontend.pynestml_frontend import to_nest, install_nest


THESIS_HOME = "/home/name/thesis"

NESTML_HOME_SUFFIX = "/eclipse/workspace/nestml"
NESTSIM_INSTALL_SUFFIX = "/nest-simulator/build_master_nompi/install"

NESTML_HOME = THESIS_HOME + NESTML_HOME_SUFFIX
NESTSIM_HOME = THESIS_HOME + NESTSIM_INSTALL_SUFFIX

GEN_DIR = os.path.join(NESTML_HOME, "generated")
MODEL_FILE = os.path.join(NESTML_HOME, "models/iaf_psc_exp.nestml")

#cleanup
try:
    rmtree(GEN_DIR)
except OSError:
    print ("Cleaning up %s failed" % GEN_DIR)
else:
    print ("Successfully deleted the %s and its contents" % GEN_DIR)

#fresh dir
try:
    os.mkdir(GEN_DIR)
except OSError:
    print ("Creation of directory %s failed" % GEN_DIR)
else:
    print ("Successfully created directory %s " % GEN_DIR)
    
to_nest(input_path=MODEL_FILE, target_path=GEN_DIR)
install_nest(GEN_DIR, NESTSIM_HOME)




# inside nest it would be
# nest.Install("nestmlmodule")
# nest.Create("cm_main")
# nest.Simulate(400.)
#...















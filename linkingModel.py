import os
from shutil import rmtree 
from pathlib import Path
from pynestml.frontend.pynestml_frontend import to_nest, install_nest

"""
This file is intended to help with testing
to see if generation and compilation works

You must edit NESTSIM_HOME variable such that it points to your nest location
"""

NESTML_HOME = os.getcwd()
NESTML_MODELS_HOME = os.path.join(NESTML_HOME, "models")
GEN_DIR = os.path.join(NESTML_HOME , "generated")

# NESTSIM_HOME: change this variable to fit nest location on your system
currentUserHome = str(Path.home())
NESTSIM_HOME = os.path.join(currentUserHome, "thesis", "nest-simulator/build_master_nompi/install")

def linkModel(nestml_model = "cm_model.nestml"):
    
    MODEL_FILE = os.path.join(NESTML_MODELS_HOME, nestml_model)
    
    #cleanup previously generated files
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
        
    to_nest(input_path=MODEL_FILE, target_path=GEN_DIR, suffix="_aaa")
    install_nest(GEN_DIR, NESTSIM_HOME)
    
    # inside nest it would be
    # nest.Install("nestmlmodule")
    # nest.Create("cm_main")
    # nest.Simulate(400.)
    #...

# random examples to try
# linkModel("cm_model.nestml")
# linkModel("hh_cond_exp_traub.nestml")

#comment this out if you don't want to test linking of all existing models
for filename in os.listdir(NESTML_MODELS_HOME):
    if filename.endswith(".nestml"): #and filename not in ("hh_cond_exp_traub.nestml",): 
        print(f"-------------- linking {filename}")
        linkModel(filename)
        print(f"-------------- linking {filename} finished")
        















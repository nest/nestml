import os
from shutil import rmtree 
from pynestml.frontend.pynestml_frontend import to_nest, install_nest

NESTML_HOME = os.getcwd()
NESTML_MODELS_HOME = os.path.join(NESTML_HOME, "models")
GEN_DIR = os.path.join(NESTML_HOME , "generated")
NESTSIM_HOME = os.path.join("/home/name/thesis", "nest-simulator/build_master_nompi/install")

def linkModel(nestml_model = "cm_model.nestml"):
    
    # MODEL_FILE = os.path.join(NESTML_HOME, "models/iaf_psc_exp.nestml")
    MODEL_FILE = os.path.join(NESTML_MODELS_HOME, nestml_model)
    # MODEL_FILE = os.path.join(NESTML_HOME, "models/iaf_cond_beta.nestml")
    
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
        
    to_nest(input_path=MODEL_FILE, target_path=GEN_DIR, suffix="_abc")
    install_nest(GEN_DIR, NESTSIM_HOME)
    
    
    # inside nest it would be
    # nest.Install("nestmlmodule")
    # nest.Create("cm_main")
    # nest.Simulate(400.)
    #...

# linkModel("cm_model.nestml")
#linkModel("hh_cond_exp_traub.nestml")


for filename in os.listdir(NESTML_MODELS_HOME):
    if filename.endswith(".nestml"): #and filename not in ("hh_cond_exp_traub.nestml",): 
        print(f"-------------- linking {filename}")
        linkModel(filename)
        print(f"-------------- linking {filename} finished")
















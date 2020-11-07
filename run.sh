PYTHONPATH=$PYTHONPATH:/home/archels/ode-toolbox ipython3 -i PyNestML.py -- --input_path=models_for_dyad --target_path=/tmp/nestml-stdp --logging_level=INFO --target=NEST --codegen_opts=nest_codegenerator_opts.json --suffix=_nestml
#PYTHONPATH=$PYTHONPATH:/home/archels/ode-toolbox ipython3 -i PyNestML.py -- --input_path=models_for_dyad --target_path=/tmp/nestml-jit --logging_level=INFO --target=NEST --codegen_opts=nest_codegenerator_opts.json


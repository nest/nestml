import os
from spynnaker.pyNN.data import SpynnakerDataView
from python_models8 import model_binaries

# This adds the model binaries path to the paths searched by sPyNNaker
SpynnakerDataView.register_binary_search_path(
    os.path.dirname(model_binaries.__file__))

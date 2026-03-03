ifndef NEURAL_MODELLING_DIRS
    $(error NEURAL_MODELLING_DIRS is not set.  Please define NEURAL_MODELLING_DIRS (possibly by running "source setup" in the neural_modelling folder within the sPyNNaker source folder))
endif

# ----------------------------------------------------------------------
# Compute the absolute path to the directory containing this file.
#
EXTRA_MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))

# ----------------------------------------------------------------------
# Make sure that APP_OUTPUT_DIR points to where you want the .aplx files to go.
#
APP_OUTPUT_DIR := $(abspath $(dir $(EXTRA_MAKEFILE_PATH))../../python_models8/model_binaries/)

# ----------------------------------------------------------------------
# Make sure EXTRA_SRC_DIR points to the source directory where your unmodified
# files are found.
#
EXTRA_SRC_DIR := $(abspath $(dir $(EXTRA_MAKEFILE_PATH))/../src/)

# ----------------------------------------------------------------------
# Add EXTRA_SRC_DIR to the SOURCE_DIRS to ensure that it gets used correctly
SOURCE_DIRS += $(EXTRA_SRC_DIR)
CFLAGS += -I$(EXTRA_SRC_DIR)

# ----------------------------------------------------------------------
# Make sure each neuron model has a unique build directory.
#
BUILD_DIR := $(abspath $(dir $(EXTRA_MAKEFILE_PATH))/../build/$(APP))/

# ----------------------------------------------------------------------
# Import the main Makefile
include $(NEURAL_MODELLING_DIRS)/makefiles/neuron_only/neuron_build.mk

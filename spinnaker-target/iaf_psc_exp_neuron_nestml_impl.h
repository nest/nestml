#ifndef _IAF_PSC_EXP_NEURON_NESTML_IMPL_
#define _IAF_PSC_EXP_NEURON_NESTML_IMPL_

#include <math.h>
#include <stdbool.h>
#include <neuron/implementations/neuron_impl.h>
#include <spin1_api.h>
#include <debug.h>

// uncomment the next line to enable printing of detailed debug information
// #define DEBUG



#define I_SYN_EXC_RECORDING_INDEX 0
#define I_SYN_INH_RECORDING_INDEX 1
#define REFR_T_RECORDING_INDEX 2
#define V_M_RECORDING_INDEX 3
//! Number of recorded state variables
#define N_RECORDED_VARS 4

#define SPIKE_RECORDING_BITFIELD 0
#define N_BITFIELD_VARS 1
//TODO: Spinnaker specific includes
// Recording defines must be done before this
#include <neuron/neuron_recording.h>
//#include <neuron/current_sources/current_source_impl.h>
//#include <neuron/current_sources/current_source.h>




// Missing paired_synapse stuff here

/**
   * Synapse types to connect to
   * @note Excluded lower and upper bounds are defined as MIN_, MAX_.
   *       Excluding port 0 avoids accidental connections.
  **/
const long MIN_SPIKE_RECEPTOR = 1;

enum input_indices
{
    EXC_SPIKES = 0,
    IGNORE_SPIKES = 1,
    I_STIM = 2,

};

typedef struct {

// 0: exc, 1: inh, 2: Istim
    REAL inputs[3];
} neuron_input_t;

typedef struct {
// State variables of the neuron
    REAL I_syn_exc;
    REAL I_syn_inh;
    REAL refr_t;
    REAL V_m;
} neuron_state_t;

typedef struct {
    // Parameters of the neuron
    REAL C_m;
    REAL E_L;
    REAL I_e;
    REAL refr_T;
    REAL tau_m;
    REAL tau_syn_exc;
    REAL tau_syn_inh;
    REAL V_reset;
    REAL V_th;

    // Internals of the neuron
    REAL __h;
    REAL __P__I_syn_exc__I_syn_exc;
    REAL __P__I_syn_inh__I_syn_inh;
    REAL __P__refr_t__refr_t;
    REAL __P__V_m__I_syn_exc;
    REAL __P__V_m__I_syn_inh;
    REAL __P__V_m__V_m;
    REAL unit_psc;
} neuron_parameter_t;

//! neuron_impl_t struct
typedef struct neuron_impl_t {
    neuron_input_t input;
    neuron_state_t state;
    neuron_parameter_t parameter;
} neuron_impl_t;

// TODO: implement gsl solver support and find out where to put gsl
/***
***/



//! Array of neuron states
static neuron_impl_t *neuron_array;

__attribute__((unused)) // Marked unused as only used sometimes
static bool neuron_impl_initialise(uint32_t n_neurons) {
#ifdef DEBUG
    log_info("[NESTML neuron] neuron_impl_initialise()");
#endif

    // Allocate DTCM for neuron array
    if (sizeof(neuron_impl_t) != 0) {
        neuron_array = spin1_malloc(n_neurons * sizeof(neuron_impl_t));
        if (neuron_array == NULL) {
            log_error("Unable to allocate neuron array - Out of DTCM");
            return false;
        }
    }

    return true;
}

__attribute__((unused)) // Marked unused as only used sometimes
static void neuron_impl_load_neuron_parameters(
        address_t address, uint32_t next, uint32_t n_neurons, address_t save_initial_state) {
    // Copy parameters to DTCM from SDRAM
    spin1_memcpy(neuron_array, &address[next],
            n_neurons * sizeof(neuron_impl_t));
    // If we are to save the initial state, copy the whole of the parameters
    // to the initial state
    if (save_initial_state) {
        spin1_memcpy(save_initial_state, neuron_array,
                n_neurons * sizeof(neuron_impl_t));
    }
}

__attribute__((unused)) // Marked unused as only used sometimes
static void neuron_impl_store_neuron_parameters(
        address_t address, uint32_t next, uint32_t n_neurons) {
    // Copy parameters to SDRAM from DTCM
    spin1_memcpy(&address[next], neuron_array,
            n_neurons * sizeof(neuron_impl_t));
}

// -------------------------------------------------------------------------
//   Methods corresponding to onReceive blocks
// -------------------------------------------------------------------------
void on_receive_block_exc_spikes(neuron_state_t *state, neuron_input_t *input, neuron_parameter_t *parameter)
{
#ifdef DEBUG
    log_info("[NESTML neuron] on_receive_block_exc_spikes()\n");
#endif

//log_info("[NESTML neuron] before update: state->I_syn_exc = 0x%x\n", state->I_syn_exc);
//log_info("[NESTML neuron] input->inputs[EXC_SPIKES] = 0x%x\n", input->inputs[EXC_SPIKES]);
//log_info("[NESTML neuron] (0.001 * input->inputs[EXC_SPIKES]) * 1000.0 = 0x%x\n", (0.001 * input->inputs[EXC_SPIKES]) * 1000.0);

//log_info("[NESTML neuron] parameter->unit_psc = 0x%x\n", parameter->unit_psc);


    state->I_syn_exc += input->inputs[EXC_SPIKES];


//log_info("[NESTML neuron] after update: state->I_syn_exc = %k\n", state->I_syn_exc);

}

// This handles incoming input events (spike and additional inputs e.g. current)
__attribute__((unused)) // Marked unused as only used sometimes
static void neuron_impl_add_inputs(
        index_t synapse_type_index, index_t neuron_index,
        input_t weights_this_timestep) {

    neuron_impl_t *neuron = &neuron_array[neuron_index];
    neuron_input_t *input = &neuron->input;

    // store the inputs for the next state update
log_info("[NESTML neuron] neuron_impl_add_inputs, weight = 0x%x = %k\n", weights_this_timestep, weights_this_timestep);
    input->inputs[synapse_type_index] += weights_this_timestep;
}

__attribute__((unused)) // Marked unused as only used sometimes
static void neuron_impl_do_timestep_update(uint32_t timer_count, uint32_t time, uint32_t n_neurons) {

#ifdef DEBUG
    log_info("[NESTML neuron] neuron_impl_do_timestep_update()\n");
#endif

    for (uint32_t neuron_index = 0; neuron_index < n_neurons; neuron_index++) {
        // Get the neuron itself
        neuron_impl_t *neuron = &neuron_array[neuron_index];
        neuron_state_t *state = &neuron->state;
        neuron_input_t *input = &neuron->input;
        neuron_parameter_t *parameter = &neuron->parameter;

        // Store the recorded membrane voltage
        neuron_recording_record_accum(V_M_RECORDING_INDEX, neuron_index, state->V_m);
        neuron_recording_record_accum(REFR_T_RECORDING_INDEX, neuron_index, state->refr_t);
        neuron_recording_record_accum(I_SYN_EXC_RECORDING_INDEX, neuron_index, state->I_syn_exc);
        neuron_recording_record_accum(I_SYN_INH_RECORDING_INDEX, neuron_index, state->I_syn_inh);
        // -------------------------------------------------------------------------
        // Begin generated code for the neuron update block
        // -------------------------------------------------------------------------
        if (state->refr_t > 0)
        {  
          // start rendered code for integrate_odes(I_syn_exc, I_syn_inh, refr_t)
          // analytic solver: integrating state variables I_syn_exc, I_syn_inh, refr_t (first step: compute new values)
          const REAL I_syn_exc__tmp = state->I_syn_exc * parameter->__P__I_syn_exc__I_syn_exc;
          const REAL I_syn_inh__tmp = state->I_syn_inh * parameter->__P__I_syn_inh__I_syn_inh;
          const REAL refr_t__tmp = parameter->__P__refr_t__refr_t * state->refr_t - 1. * parameter->__h;
          // analytic solver: integrating state variables I_syn_exc, I_syn_inh, refr_t (second step: replace analytically solvable variables with precisely integrated values)
          state->I_syn_exc = I_syn_exc__tmp;
          state->I_syn_inh = I_syn_inh__tmp;
          state->refr_t = refr_t__tmp;
          // end rendered code for integrate_odes(I_syn_exc, I_syn_inh, refr_t)
        }
        else
        {  
          // start rendered code for integrate_odes(I_syn_exc, I_syn_inh, V_m)
          // analytic solver: integrating state variables I_syn_exc, I_syn_inh, V_m (first step: compute new values)
          const REAL I_syn_exc__tmp = state->I_syn_exc * parameter->__P__I_syn_exc__I_syn_exc;
          const REAL I_syn_inh__tmp = state->I_syn_inh * parameter->__P__I_syn_inh__I_syn_inh;
          const REAL V_m__tmp = (-parameter->E_L) * parameter->__P__V_m__V_m + parameter->E_L + state->I_syn_exc * parameter->__P__V_m__I_syn_exc + state->I_syn_inh * parameter->__P__V_m__I_syn_inh + state->V_m * parameter->__P__V_m__V_m - parameter->I_e * parameter->__P__V_m__V_m * parameter->tau_m / parameter->C_m + parameter->I_e * parameter->tau_m / parameter->C_m - input->inputs[I_STIM] * parameter->__P__V_m__V_m * parameter->tau_m / parameter->C_m + input->inputs[I_STIM] * parameter->tau_m / parameter->C_m;
          // analytic solver: integrating state variables I_syn_exc, I_syn_inh, V_m (second step: replace analytically solvable variables with precisely integrated values)
          state->I_syn_exc = I_syn_exc__tmp;
          state->I_syn_inh = I_syn_inh__tmp;
          state->V_m = V_m__tmp;
          // end rendered code for integrate_odes(I_syn_exc, I_syn_inh, V_m)
        }
        // -------------------------------------------------------------------------
        // Begin NESTML generated code for invoking the onReceive block(s)
        // -------------------------------------------------------------------------

        if (input->inputs[EXC_SPIKES])
        {
            on_receive_block_exc_spikes(state, input, parameter);
        }


        // -------------------------------------------------------------------------
        // Begin NESTML generated code for the onCondition block(s)
        // -------------------------------------------------------------------------
        if (state->refr_t <= 0 && state->V_m >= parameter->V_th)
        {
            state->refr_t = parameter->refr_T;
            state->V_m = parameter->V_reset;

            // begin generated code for emit_spike() function

            neuron_recording_record_bit(SPIKE_RECORDING_BITFIELD, neuron_index);
            send_spike(timer_count, time, neuron_index);
            // end generated code for emit_spike() function
        }
        input->inputs[EXC_SPIKES] = ZERO;
        input->inputs[IGNORE_SPIKES] = ZERO;
        input->inputs[I_STIM] = ZERO;
    }
}

#if LOG_LEVEL >= LOG_DEBUG
void neuron_impl_print_inputs(uint32_t n_neurons) {
    log_debug("-------------------------------------\n");
    for (index_t i = 0; i < n_neurons; i++) {
        neuron_impl_t *neuron = &neuron_array[i];
        neuron_input_t *input = &neuron.input;

        log_debug("inputs: %k %k", input->inputs[0], input->inputs[1]);
    }
    log_debug("-------------------------------------\n");
}

void neuron_impl_print_synapse_parameters(uint32_t n_neurons) {
    // there aren't any accessible in this example
    use(n_neurons);
}

const char *neuron_impl_get_synapse_type_char(uint32_t synapse_type) {
    use(synapse_type);
    return 0;
}
#endif // LOG_LEVEL >= LOG_DEBUG


#endif // _IAF_PSC_EXP_NEURON_NESTML_IMPL_
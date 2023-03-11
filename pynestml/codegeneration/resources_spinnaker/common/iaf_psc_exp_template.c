#include <iaf_psc_exp_template.h>

// -------------------------------------------------------------------------
//  Globals
// -------------------------------------------------------------------------

static iaf_psc_exp * neuron_array;

// -------------------------------------------------------------------------
//  Constructors
// -------------------------------------------------------------------------

void Parameters_init() {

};

void State_init() {

};

void Variables_init() {

};

void Buffers_init(iaf_psc_exp * neuron) {

};

void Buffers_init(const struct Buffers_ * buffer, iaf_psc_exp * neuron) {

};

void iaf_psc_exp_init () {

};

void iaf_psc_exp_copy_init (const iaf_psc_exp * neuron) {

};

// -------------------------------------------------------------------------
//  Functions
// -------------------------------------------------------------------------

void recompute_internal_variables (bool exlude_timestep) {

};

__attribute__((unused))
static bool neuron_impl_initialise (uint32_t n_neurons) {
    // Allocate DTCM for neuron array
    if (sizeof(iaf_psc_exp) != 0) {
        neuron_array = spin1_malloc(n_neurons * sizeof(iaf_psc_exp));
        if (neuron_array == NULL) {
            log_error("Unable to allocate neuron array - Out of DTCM");
            return false;
        }
    }
    return true;
};

__attribute__((unused))
static void neuron_impl_load_neuron_parameters (
        address_t address,
        uint32_t next,
        uint32_t n_neurons,
        address_t save_initial_state) {

    // Copy parameters to DTCM from SDRAM
    spin1_memcpy(neuron_array, &address[next], n_neurons * sizeof(iaf_psc_exp));
    // If we are to save the initial state, copy the whole of the parameters
    // to the initial state
    if (save_initial_state) {
        spin1_memcpy(save_initial_state, neuron_array, n_neurons * sizeof(iaf_psc_exp));
    }

};

__attribute__((unused))
static void neuron_impl_store_neuron_parameters (
        address_t address,
        uint32_t next,
        uint32_t n_neurons) {
    // Copy parameters to SDRAM from DTCM
    spin1_memcpy(&address[next], neuron_array, n_neurons * sizeof(iaf_psc_exp));

};


__attribute__((unused))
static void neuron_impl_add_inputs (
        index_t synapse_type_index,
        index_t neuron_index,
        input_t weights_this_timestep){
    
    // Get the neuron itself
    iaf_psc_exp *neuron = &neuron_array[neuron_index];

    // Do something to store the inputs for the next state update
    neuron->inputs[synapse_type_index] += weights_this_timestep;
};

__attribute__((unused))
static void neuron_impl_do_timestep_update (
        uint32_t timer_count,
        uint32_t time,
        uint32_t n_neurons){
    for (uint32_t neuron_index = 0; neuron_index < n_neurons; neuron_index++) {
        // Get the neuron itself
        iaf_psc_exp *neuron = &neuron_array[neuron_index];

        // Store the recorded membrane voltage
        neuron_recording_record_accum(V_RECORDING_INDEX, neuron_index, neuron->v);

        // Do something to update the state
        neuron->v += neuron->inputs[0] - neuron->inputs[1];
        neuron->inputs[0] = ZERO;
        neuron->inputs[1] = ZERO;

        // Determine if the neuron has spiked
        if (neuron->v > neuron->threshold) {
            // Reset if spiked
            neuron->v = ZERO;
            neuron_recording_record_bit(SPIKE_RECORDING_BITFIELD, neuron_index);
            send_spike(timer_count, time, neuron_index);
        }
    }
};


#if LOG_LEVEL >= LOG_DEBUG
__attribute__((unused))
static void neuron_impl_print_inputs (uint32_t n_neurons) {
    log_debug("-------------------------------------\n");
    for (index_t i = 0; i < n_neurons; i++) {
        iaf_psc_exp *neuron = &neuron_array[i];
        log_debug("inputs: %k %k", neuron->inputs[0], neuron->inputs[1]);
    }
    log_debug("-------------------------------------\n");
};

__attribute__((unused))
static void neuron_impl_print_synapse_parameters (uint32_t n_neurons) {
    // there aren't any accessible in this example
    use(n_neurons);
};

__attribute__((unused))
static const char *neuron_impl_get_synapse_type_char (uint32_t synapse_type) {
    use(synapse_type);
    return 0;
};

#endif

// Interesting template in NewModelTemplate/c_models/src/my_models/playsticity/stdp/timing_dependence/my_timing.h => _timing_impl.h
// maybe this s not necessaryif we just base the synapse on 'synapse_dynamics_stdp_mad_impl.c' which implements as a synapse base class
// alternatively we could copy that file here for changes

// The current for the models makefile must be named the same as the put toghether name from python, where synaps dynamics timing and weight is added to the name.
// we also have to change the synapse_build.mk when we want to use a single module


/*** COMMON INCLUDES ***/
#include <debug.h>
#include <neuron/plasticity/stdp/maths.h>
#include <spin1_api.h>
#include <utils.h>
#include <stddef.h>
#include <static-assert.h>
#include <neuron/plasticity/stdp/stdp_typedefs.h>

/*** SYSTEM INCLUDES ***/
#include <neuron/synapses.h> // => Used in system
#include <neuron/synapse_row.h> // => Used in system
/* Structure for one synapse, called row
 * |       Weight      |       Delay      |  Synapse Type   |   Neuron Index   |
 * |-------------------|------------------|-----------------|------------------|
 * |SYNAPSE_WEIGHT_BITS|SYNAPSE_DELAY_BITS|SYNAPSE_TYPE_BITS|SYNAPSE_INDEX_BITS|
 * |                   |                  |       SYNAPSE_TYPE_INDEX_BITS      |
 */

/*** POST EVENTS ***/
// API for pre and post spike processing and data structures, independent of system
#include <neuron/plasticity/stdp/post_events.h>

/*** SYNAPSE STRUCTURE ***/
// API for state management of synapse, mostly independet of system
#include <neuron/plasticity/stdp/synapse_structure/synapse_structure.h>

/*** SYNAPSE DYNAMICS***/
// For implementation of this API see synapse_dynamics_stdp_common and synapse_dynamics_stdp_mad_impl
#include <neuron/plasticity/synapse_dynamics.h>

/*** TIMING DEPENDENCE ***/
// API for timing implementation, independent of system
#include <neuron/plasticity/stdp/timing_dependence/timing.h>


/*** WEIGHT DEPENDENCE ***/
// API for weight implementation, independent of system
#include <neuron/plasticity/stdp/weight_dependence/weight.h>
// We can ommit this, adds API for depression and potentiation, independet of system
#include <neuron/plasticity/stdp/weight_dependence/weight_one_term.h>


/*** DATA STRUCTURES ***/

//Used only by us
typedef struct stdp_params {
} stdp_params;

// Fixed parameters of synapse
//Used only by us
typedef struct fixed_stdp_synapse {
} fixed_stdp_synapse;

//Used only by us
typedef struct {
} pre_event_history_t;

//Used only by us
typedef struct {
} post_event_history_t;

//Used only by us
typedef struct {
} post_event_window_t;

// Parameters shared by all weights => modify for synapses
//Used only by us
typedef struct {
} plasticity_weight_region_data_t;

//Intermediate datastructure for eg. updating = more bits => modify for synapse
//Used only by us
typedef struct {
} weight_state_t;

//Used only by us
typedef struct post_trace_t {
} post_trace_t;

//Used only by us
typedef struct pre_trace_t {
} pre_trace_t;

//Used only by us
typedef struct my_timing_config {
} my_timing_config_t;


/*** TYPE DEFS ***/
// weight_t from synapse_row.h (uint of size SYNAPSE_WEIGHT_BITS: DEFAULT 16)
// => First bits of synapse row

// Below only when only using weight
//Used only by us
typedef weight_t plastic_synapse_t;
//Used only by us
typedef weight_state_t update_state_t;
//Used only by us
typedef weight_t final_state_t;


/*** POST EVENTS ***/
// => All methods from the timing API are called only by us 

//Called only by us
static inline void print_event_history(const post_event_history_t *events) {
}

//Called only by us
static inline post_event_history_t *post_events_init_buffers(
        uint32_t n_neurons) {
}

// Setup a window pointing to first event in window, linking to previous event and counting all events in window
//Called only by us
static inline post_event_window_t post_events_get_window_delayed(
        const post_event_history_t *events, uint32_t begin_time,
        uint32_t end_time) {
}

// Return next event in window
//Called only by us
static inline post_event_window_t post_events_next(
        post_event_window_t window) {
}

// Add event and time to buffer, drop oldest event if buffer is full
//Called only by us
static inline void post_events_add(
        uint32_t time, post_event_history_t *events, post_trace_t trace) {

}


//Called only by us 
static inline void print_delayed_window_events(
        const post_event_history_t *post_event_history,
        uint32_t begin_time, uint32_t end_time, uint32_t delay_dendritic) {
    
}

/*** SYNAPSE STRUCTURE ***/
// => All methods from the timing API are called only by us 

// Translate from 16 bit to 32 bit for computing updates
//Called only by us 
static update_state_t synapse_structure_get_update_state(
        plastic_synapse_t synaptic_word, index_t synapse_type);

// Translate updated state from 32 bit to 16 bit
//Called only by us 
static final_state_t synapse_structure_get_final_state(
        update_state_t state);

// Extract weight from final state
//Called only by us
static weight_t synapse_structure_get_final_weight(
        final_state_t final_state);

// Translate from state to synapse word -> could be the same data structure
//Called only by us
static plastic_synapse_t synapse_structure_get_final_synaptic_word(
        final_state_t final_state);

// Initialise state
//Called only by us, weight_t not defined by us
static plastic_synapse_t synapse_structure_create_synapse(weight_t weight);

// Extract weight
//Called only by us, weight_t not defined by us
static weight_t synapse_structure_get_weight(plastic_synapse_t synaptic_word);

// Rely on implementation of weight dependece to decay
//Called only by us
static void synapse_structure_decay_weight(update_state_t *state, uint32_t decay);

// Rely on implementation in weight dependece to update weight
//Called only by us
static accum synapse_structure_get_update_weight(update_state_t state);


/*** SYNAPTIC DYNAMICS ***/
// => Entrypoint for system calls

//System called (c_main_synapse_common.h)
bool synapse_dynamics_initialise(
        address_t address, uint32_t n_neurons, uint32_t n_synapse_types,
        uint32_t *ring_buffer_to_input_buffer_left_shifts);

//System called (synapses.c)
bool synapse_dynamics_process_plastic_synapses(
        synapse_row_plastic_data_t *plastic_region_data,
        synapse_row_fixed_part_t *fixed_region,
        weight_t *ring_buffers, uint32_t time, uint32_t colour_delay,
        bool *write_back);

//System called (send_spike.h)
void synapse_dynamics_process_post_synaptic_event(
        uint32_t time, index_t neuron_index);


//System called (synapses.c)
void synapse_dynamics_print_plastic_synapses(
        synapse_row_plastic_data_t *plastic_region_data,
        synapse_row_fixed_part_t *fixed_region,
        uint32_t *ring_buffer_to_input_buffer_left_shifts);

//System called (synapses.c)
uint32_t synapse_dynamics_get_plastic_pre_synaptic_events(void);

//System called (c_main_synapse_common.h)
uint32_t synapse_dynamics_get_plastic_saturation_count(void);

//Border zone (topographic_map_impl.c) -> neuromodulation only
bool synapse_dynamics_find_neuron(
        uint32_t id, synaptic_row_t row, weight_t *weight, uint16_t *delay,
        uint32_t *offset, uint32_t *synapse_type);

//Border zone (sp_structs.h) -> neuromodulation only
bool synapse_dynamics_remove_neuron(uint32_t offset, synaptic_row_t row);

//Border zone (sp_structs.h) -> neuromodulation only
bool synapse_dynamics_add_neuron(
        uint32_t id, synaptic_row_t row, weight_t weight,
        uint32_t delay, uint32_t type);

//Border zone (topographic_map_impl.c) -> neuromodulation only
uint32_t synapse_dynamics_n_connections_in_row(synapse_row_fixed_part_t *fixed);


/*** WEIGHT DEPENDENCE ***/
// => All methods from the timing API are called only by us 

//Called only by us
address_t weight_initialise(
    address_t address, 
    uint32_t n_synapse_types, 
    uint32_t *ring_buffer_to_input_buffer_leftshift);

//Called only by us, weight_t not defined by us
static inline weight_state_t weight_get_initial(
        weight_t weight, index_t synapse_type) {

}

// Intermediate store depression
// Called only by us
static inline weight_state_t weight_one_term_apply_depression(
        weight_state_t state, int32_t depression) {

}

// Intermediate store potentiation
// Called only by us
static inline weight_state_t weight_one_term_apply_potentiation(
        weight_state_t state, int32_t potentiation) {


}

// Apply potentiation and depression to weight and return
//Called only by us, weight_t not defined by us 
static inline weight_t weight_get_final(weight_state_t new_state) {

}

//Called only by us 
__attribute__((unused)) // Marked unused as only used sometimes
static void weight_decay(weight_state_t *state, int32_t decay) {
}

//Called only by us
__attribute__((unused)) // Marked unused as only used sometimes
static accum weight_get_update(weight_state_t state) {

}


/*** TIMING DEPENDENCE ***/
// => All methods from the timing API are called only by us 

//Called only by us
address_t timing_initialise(address_t address);

//Called only by us
static inline post_trace_t timing_get_initial_post_trace(void) {

}

//Called only by us
static inline post_trace_t timing_add_post_spike(
        uint32_t time, uint32_t last_time, post_trace_t last_trace) {

}

//Called only by us
static inline pre_trace_t timing_add_pre_spike(
        uint32_t time, uint32_t last_time, pre_trace_t last_trace) {

}

//Called only by us
static inline update_state_t timing_apply_pre_spike(
        uint32_t time, pre_trace_t trace, uint32_t last_pre_time,
        pre_trace_t last_pre_trace, uint32_t last_post_time,
        post_trace_t last_post_trace, update_state_t previous_state) {
}

//Called only by us
static inline update_state_t timing_apply_post_spike(
        uint32_t time, post_trace_t trace, uint32_t last_pre_time,
        pre_trace_t last_pre_trace, uint32_t last_post_time,
        post_trace_t last_post_trace, update_state_t previous_state) {
}

//Called only by us 
static post_trace_t timing_decay_post(
        uint32_t time, uint32_t last_time, post_trace_t last_trace) {
}
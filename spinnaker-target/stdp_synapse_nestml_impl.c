/**
 *  stdp_synapse_nestml_impl.c
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 *  Generated from NESTML 8.3.0-rc3-post-dev at time: 2026-07-14 18:14:09.166925
**/

#include "stdp_synapse_nestml_impl.h"

// uncomment the next line to enable printing of detailed debug information
//#define DEBUG

// uncomment the next line to enable printing of very detailed debug information (could overflow ITCM)
//#define PLOT_DETAILED_STATE
//#define PLOT_DETAILED_STATE
#define PLOT_DETAILED_STATE2


// global plasticity parameter data (in DTCM)
plasticity_weight_region_data_t *plasticity_weight_region_data;


extern uint32_t skipped_synapses;



// plasticity multiply shift array, in DTCM
uint32_t *weight_shift;




uint64_t _udiv64(uint64_t num, uint64_t den) {

    uint64_t quot = 0;
    uint64_t qbit = 1;

    if (den == 0) {
        /* Intentional divide by zero, without
	       triggering a compiler warning which
	       would abort the build */
        return 1/((unsigned)den);
    }

    /* Left-justify denominator and count shift */
    while ((int64_t) den >= 0) {
        den <<= 1;
        qbit <<= 1;
    }

    while (qbit) {
        if (den <= num) {
            num -= den;
            quot += qbit;
        }
        den >>= 1;
        qbit >>= 1;
    }
    return quot;
}




//static inline accum _kdivk(accum a, accum b) {
accum _kdivk(accum a, accum b) {
    if (a < 0k && b < 0k) {
        const accum ret = _kdivk(-1k * a, -1k * b);
//        log_info("\t\tkdivk: (1) returning %k / %k = 0x%x = %k", a, b, ret, ret);
        return ret;
    }

    if (a < 0k) {
        const accum ret = -1k * _kdivk(-1k * a, b);
//        log_info("\t\tkdivk: (2) returning %k / %k = 0x%x = %k", a, b, ret, ret);
        return ret;
    }

    if (b < 0k) {
        const accum ret = -1k * _kdivk(a, -1k * b);
//        log_info("\t\tkdivk: (3) returning %k / %k = 0x%x = %k", a, b, ret, ret);
        return ret;
    }

    const accum ret = kbits((uint32_t)_udiv64(((uint64_t) bitsk(a) << 15), (uint64_t) bitsk(b)));
//    log_info("\t\tkdivk: (4) returning %k / %k = 0x%x = %k", a, b, ret, ret);

    return ret;
}


bool synapse_dynamics_initialise(
        address_t address, uint32_t n_neurons, uint32_t n_synapse_types,
        uint32_t *ring_buffer_to_input_buffer_left_shifts) {

    char _string_buf[20];

    log_info("[NESTML synapse] In synapse_dynamics_initialise(n_neurons = %d, n_synapse_types = %d)", n_neurons, n_synapse_types);

    // Weight shift between synapse-state-internal weight representation (S1615) and the representation in the way it needs to be written into the ring buffer. Number of bits to shift by is determined using heuristics at runtime by SpiNNaker software stack; this needs to be stored for each individual synapse type
    weight_shift = spin1_malloc(sizeof(uint32_t) * n_synapse_types);
    if (weight_shift == NULL) {
        log_error("Could not initialise weight region data");
        return NULL;
    }

    for (uint32_t s = 0; s < n_synapse_types; ++s) {
        weight_shift[s] = ring_buffer_to_input_buffer_left_shifts[s];
//#ifdef DEBUG
        log_info("\t[NESTML synapse] \tSynapse type %u: weight shift = %d\n", s, weight_shift[s]);
//#endif
    }

    // load parameters
    plasticity_weight_region_data_t *config = (plasticity_weight_region_data_t*)address;
    plasticity_weight_region_data = spin1_malloc(sizeof(plasticity_weight_region_data_t) * n_synapse_types);

    if (plasticity_weight_region_data == NULL) {
        log_error("Could not initialise weight region data");
        return false;
    }

    for (uint32_t s = 0; s < 1; s++, config++) {  // XXX: only permit one synapse type for now
        plasticity_weight_region_data[s].d = config->d;
#ifdef DEBUG
//        log_info("\t[NESTML synapse] \tSynapse type %u: Parameter d, Raw value: %x, Value: %k", s, plasticity_weight_region_data[s].d, plasticity_weight_region_data[s].d);
#endif
        plasticity_weight_region_data[s].lambda = config->lambda;
#ifdef DEBUG
//        log_info("\t[NESTML synapse] \tSynapse type %u: Parameter lambda, Raw value: %x, Value: %k", s, plasticity_weight_region_data[s].lambda, plasticity_weight_region_data[s].lambda);
#endif
        plasticity_weight_region_data[s].alpha = config->alpha;
#ifdef DEBUG
//        log_info("\t[NESTML synapse] \tSynapse type %u: Parameter alpha, Raw value: %x, Value: %k", s, plasticity_weight_region_data[s].alpha, plasticity_weight_region_data[s].alpha);
#endif
        plasticity_weight_region_data[s].tau_tr_pre = config->tau_tr_pre;
#ifdef DEBUG
//        log_info("\t[NESTML synapse] \tSynapse type %u: Parameter tau_tr_pre, Raw value: %x, Value: %k", s, plasticity_weight_region_data[s].tau_tr_pre, plasticity_weight_region_data[s].tau_tr_pre);
#endif
        plasticity_weight_region_data[s].tau_tr_post = config->tau_tr_post;
#ifdef DEBUG
//        log_info("\t[NESTML synapse] \tSynapse type %u: Parameter tau_tr_post, Raw value: %x, Value: %k", s, plasticity_weight_region_data[s].tau_tr_post, plasticity_weight_region_data[s].tau_tr_post);
#endif
        plasticity_weight_region_data[s].mu_plus = config->mu_plus;
#ifdef DEBUG
//        log_info("\t[NESTML synapse] \tSynapse type %u: Parameter mu_plus, Raw value: %x, Value: %k", s, plasticity_weight_region_data[s].mu_plus, plasticity_weight_region_data[s].mu_plus);
#endif
        plasticity_weight_region_data[s].mu_minus = config->mu_minus;
#ifdef DEBUG
//        log_info("\t[NESTML synapse] \tSynapse type %u: Parameter mu_minus, Raw value: %x, Value: %k", s, plasticity_weight_region_data[s].mu_minus, plasticity_weight_region_data[s].mu_minus);
#endif
        plasticity_weight_region_data[s].Wmin = config->Wmin;
#ifdef DEBUG
//        log_info("\t[NESTML synapse] \tSynapse type %u: Parameter Wmin, Raw value: %x, Value: %k", s, plasticity_weight_region_data[s].Wmin, plasticity_weight_region_data[s].Wmin);
#endif
        plasticity_weight_region_data[s].Wmax = config->Wmax;
#ifdef DEBUG
//        log_info("\t[NESTML synapse] \tSynapse type %u: Parameter Wmax, Raw value: %x, Value: %k", s, plasticity_weight_region_data[s].Wmax, plasticity_weight_region_data[s].Wmax);
#endif
    }

    post_event_history = post_events_init_buffers(n_neurons);
    if (post_event_history == NULL) {
        return false;
    }

    return true;
}

//---------------------------------------
// Synaptic row plastic-region implementation
//---------------------------------------
void synapse_dynamics_print_plastic_synapses(
        synapse_row_plastic_data_t *plastic_region_data,
        synapse_row_fixed_part_t *fixed_region,
        uint32_t *ring_buffer_to_input_buffer_left_shifts) {

    return;

    __use(plastic_region_data);
    __use(fixed_region);
    __use(ring_buffer_to_input_buffer_left_shifts);
}

//---------------------------------------
//! \brief Get the axonal delay
//! \param[in] x: The packed plastic synapse control word
//! \return the axonal delay
static inline index_t sparse_axonal_delay(uint32_t x) {
#if 1
    // No axonal delay, ever
    __use(x);
    return 0;
#else
    return (x >> synapse_delay_index_type_bits) & SYNAPSE_AXONAL_DELAY_MASK;
#endif
}



static void update_internal_state_(synapse_state_t *state, uint32_t t_start, uint32_t timestep) {

    /**
     * Recompute propagator constants
    **/

    const accum __h = timestep;   // XXX: time constants are in ms, so __h should be as well! convert uint32_t to accum type

    log_info("[NESTML synapse] update_internal_state_(__h = %d)\n", timestep);

    if (timestep == 0) {
        return;
    }

    /**
     * Begin NESTML generated code for the update block
    **/

//log_info("[NESTML synapse] \tintegrating __P__post_trace__post_trace = %k = 0x%x\n", __P__post_trace__post_trace, __P__post_trace__post_trace);
//log_info("[NESTML synapse] \tintegrating state->post_trace before = %k = 0x%x\n", state->post_trace, state->post_trace);
    // start rendered code for integrate_odes()
    // end rendered code for integrate_odes()

//log_info("[NESTML synapse] \tintegrating state->post_trace after = %k = 0x%x\n", state->post_trace, state->post_trace);
    /**
     * End NESTML generated code for the update block
    **/
}


static void post_spike_on_receive(synapse_state_t *state, uint32_t time, synapse_row_plastic_data_t *plastic_region_address) {
    log_info("[NESTML synapse] post_spike_on_receive(time = %d)\n", time);
    // synapse row header is defined: need to fetch certain presynaptic variables from there
    // update the state of "header" variables common to all synapses from the time of the last pre spike to the current time

    const accum __h = time - plastic_region_address->history.prev_time;   // XXX: time constants are in ms, so __h should be as well! convert uint32_t to accum type

    log_info("[NESTML synapse] \ton_address->history.prev_t = %x\n", plastic_region_address->history.prev_time);
    log_info("[NESTML synapse] \t__h = %k\n", __h);
    const accum __P__pre_trace__for__stdp_synapse_nestml__pre_trace__for__stdp_synapse_nestml = expk(_kdivk((-__h), plasticity_weight_region_data->tau_tr_pre));    // type: real
    const REAL pre_trace__for__stdp_synapse_nestml__tmp = __P__pre_trace__for__stdp_synapse_nestml__pre_trace__for__stdp_synapse_nestml * plastic_region_address->history.pre_trace__for__stdp_synapse_nestml;

    log_info("[NESTML synapse] \tpre_trace__for__stdp_synapse_nestml__tmp = %x\n", pre_trace__for__stdp_synapse_nestml__tmp);    


    /**
     *  NESTML generated onReceive code block for postsynaptic port "post_spikes" begins here!
    **/
    state->w += plasticity_weight_region_data->lambda * pre_trace__for__stdp_synapse_nestml__tmp;
    state->w = MIN(plasticity_weight_region_data->Wmax, state->w);
}


/**
 * Contains generated code for all the statements corresponding to ``onReceive(pre_spikes)`` blocks.
**/
static void pre_spike_on_receive(synapse_state_t *state, uint32_t time,const REAL post_trace__for__stdp_synapse_nestml__tmp) {

    /**
     *  NESTML generated onReceive code block for presynaptic port "pre_spikes" begins here!
    **/

  log_info("[NESTML synapse] pre_spike_on_receive(time = %d)\n", time);
//  log_info("[NESTML synapse] \tstate->w = %k (raw: 0x%x)\n", state->w, state->w);
  //log_info("[NESTML synapse] \tplasticity_weight_region_data->lambda = %k (raW: 0x%x)\n", plasticity_weight_region_data->lambda, plasticity_weight_region_data->lambda);

    
    state->w -= plasticity_weight_region_data->lambda * post_trace__for__stdp_synapse_nestml__tmp;
    state->w = MAX(plasticity_weight_region_data->Wmin, state->w);

    // begin generated code for emit_spike() function

    // end generated code for emit_spike() function

//  log_info("[NESTML synapse] \tafter state->w = %k (raw: 0x%x)\n", state->w, state->w);
}


static void process_plastic_synapse(synapse_row_plastic_data_t *plastic_region_address,
        uint32_t control_word,
        uint32_t last_pre_time,
        accum pre_trace__for__stdp_synapse_nestml,
        weight_t *ring_buffers, uint32_t pre_spike_time,
		uint32_t colour_delay, synapse_word_t *synapse_word) {

    fixed_stdp_synapse_nestml s = synapse_dynamics_stdp_get_fixed(control_word, pre_spike_time, colour_delay);

#ifdef DEBUG
    log_info("[NESTML synapse] In process_plastic_synapse(time = %d, last_pre_time = %d, dendritic_delay = %x)", pre_spike_time, last_pre_time, s.delay_dendritic);
    log_info("[NESTML synapse] \tpre_trace__for__stdp_synapse_nestml__tmp = %k = 0x%x\n", pre_trace__for__stdp_synapse_nestml__tmp, pre_trace__for__stdp_synapse_nestml__tmp);
#endif

    uint32_t post_delay = s.delay_dendritic;
    if (!params.backprop_delay) {
        post_delay = 0;
    }

    synapse_state_t state = synapse_word_to_state_t(synapse_word, plastic_synapse_word_stride);
//#ifdef PLOT_DETAILED_STATE
    log_info("[NESTML synapse] \tCurrent state:");
    log_info("[NESTML synapse] \t\tw = %k (raw: 0x%x)\n", state.w, state.w);
//#endif

    uint32_t current_time = last_pre_time; // at the start, the state is either the initial state, or however we left it when the previous pre-synaptic spike was processed

    // Apply axonal delay to time of last presynaptic spike
    const uint32_t delay_axonal = 0;
    const uint32_t delayed_last_pre_time = last_pre_time + delay_axonal;

    // Get the post-synaptic window of events to be processed
    const uint32_t window_begin_time =
            (delayed_last_pre_time >= s.delay_dendritic)
            ? (delayed_last_pre_time - s.delay_dendritic) : 0;
    const uint32_t delayed_pre_time = pre_spike_time + delay_axonal;
    const uint32_t window_end_time =
            (delayed_pre_time >= s.delay_dendritic)
            ? (delayed_pre_time - s.delay_dendritic) : 0;

    post_event_window_t post_window = post_events_get_window_delayed(&post_event_history[s.index], window_begin_time, window_end_time);
    log_info("[NESTML synapse] \t\ts.index = %u\n", s.index);

    log_info("[NESTML synapse] \t  Fetching post window from %u to %u\n", window_begin_time, window_end_time);

    // Process events in post-synaptic window
    while (post_window.num_events > 0) {
        const uint32_t delayed_post_time = *post_window.next_time + s.delay_dendritic;

#ifdef PLOT_DETAILED_STATE
        log_info("[NESTML synapse] \t\tApplying post-synaptic event at delayed time: %u\n", delayed_post_time);
#endif

        /**
         * update synapse internal state from `current_time` to `delayed_post_time`
        **/

        update_internal_state_(&state, current_time, delayed_post_time - current_time);
        current_time = delayed_post_time;

#ifdef PLOT_DETAILED_STATE
    log_info("[NESTML synapse] \tNEW state after updating internal state to t = %u", current_time);
    log_info("[NESTML synapse] \t\tw = 0x%x\n", state.w);
#endif

        /**
         * handle the postsynaptic spike
        **/

        post_spike_on_receive(&state, current_time, plastic_region_address);

#ifdef PLOT_DETAILED_STATE
    log_info("[NESTML synapse] \tNEW state after applying post spike:");
    log_info("[NESTML synapse] \t\tw = 0x%x\n", state.w);
#endif

        // Go onto next event
        post_window = post_events_next(post_window);
    }


    /**
     * update synapse internal state from the time of the last post spike (= `current_time`) to `pre_spike_time`
    **/

    update_internal_state_(&state, current_time, pre_spike_time - current_time);

#ifdef PLOT_DETAILED_STATE
    log_info("[NESTML synapse] \tNEW state after integration to t_pre:");
    log_info("[NESTML synapse] \t\tw = 0x%x\n", state.w);
#endif
    /**
     * update postsynaptic history buffer entries from the time of the last post spike (= `current_time`) to `pre_spike_time`
    **/




    // update variables in the postsynaptic header (i.e. in the post-history-buffer)
    const accum __h = pre_spike_time - current_time;   // XXX: time constants are in ms, so __h should be as well! convert uint32_t to accum type


    const accum __P__post_trace__for__stdp_synapse_nestml__post_trace__for__stdp_synapse_nestml = expk(_kdivk((-__h), plasticity_weight_region_data->tau_tr_post));    // type: real

    // propagate the state forward in time
    REAL post_trace__for__stdp_synapse_nestml__tmp = __P__post_trace__for__stdp_synapse_nestml__post_trace__for__stdp_synapse_nestml * post_trace__for__stdp_synapse_nestml__tmp;

    /**
     * execute onReceive statements in pre spike onReceive blocks
    **/

    pre_spike_on_receive(&state, pre_spike_time,post_trace__for__stdp_synapse_nestml__tmp);

#ifdef PLOT_DETAILED_STATE
    log_info("[NESTML synapse] \tNEW state after processing pre_spikes:");
    log_info("[NESTML synapse] \t\tw = 0x%x\n", state.w);
#endif
log_info("[NESTML synapse] \t\tplastic_region_address->history.pre_trace__for__stdp_synapse_nestml = %x = %k\n", plastic_region_address->history.pre_trace__for__stdp_synapse_nestml, plastic_region_address->history.pre_trace__for__stdp_synapse_nestml);

	/**
	 * Add weight to ring-buffer entry, but only if not too late
	**/

	if (s.delay_axonal + s.delay_dendritic > colour_delay) {
	    int32_t weight = TYPECAST_TO_UINT32_T(state.w);   // XXX: TODO: the variable name ``w`` is hard-coded here
	    synapse_dynamics_stdp_update_ring_buffers(ring_buffers, s, weight >> weight_shift[s.type]);
        log_info("[NESTML synapse] \tadding weight to ring-buffer entry; weight = 0x%x", weight);
    }
    else {
        skipped_synapses++;
        log_info("[NESTML synapse] \tskipping synapse");
    }

    /**
     * Encode the new state into synaptic word
    **/

    state_t_to_synapse_word(&state, synapse_word, plastic_synapse_word_stride);
//    log_info("[NESTML synapse] ---> the new synapse word is 0x%x, 0x%x, 0x%x", synapse_word->w, synapse_word->pre_trace, synapse_word->post_trace);
}


/**
 * print low-level synaptic row data
**/
void print_low_level_synaptic_row_data(synapse_row_plastic_data_t *plastic_region_address,
                                       synapse_row_fixed_part_t *fixed_region) {

#ifdef PLOT_DETAILED_STATE2
log_info("[NESTML synapse] print_low_level_synaptic_row_data()\n");
    // data words: for each synapse, stores the complete state in a 32-bit word
    synapse_word_t *plastic_words = plastic_region_address->synapses;

    // control words: for each synapse, stores the delay, synapse type, and postsynaptic neuron ID
    control_t *control_words = synapse_row_plastic_controls(fixed_region);

    // Print out parsed data for static synapses
    uint32_t *synaptic_words = synapse_row_fixed_weight_controls(fixed_region);
    const uint32_t n_fixed_synapses = synapse_row_num_fixed_synapses(fixed_region);
    log_info("[NESTML synapse] \tFixed-Fixed Region (%u synapses):", n_fixed_synapses);
    for (size_t i = 0; i < n_fixed_synapses; ++i) {
        uint32_t synaptic_word = *synaptic_words++;

        uint32_t delay = synapse_row_sparse_delay(synaptic_word, synapse_type_index_bits, synapse_delay_mask);
        uint32_t type = synapse_row_sparse_type(synaptic_word, synapse_index_bits, synapse_type_mask);
        uint32_t neuron = synapse_row_sparse_index(synaptic_word, synapse_index_mask);
        log_info("[NESTML synapse] \t\tDelay %u, Synapse Type %u, Neuron %u", delay, type, neuron);
    }

    const size_t n_plastic_synapses = synapse_row_num_plastic_controls(fixed_region);

    log_info("[NESTML synapse] \tPlastic region %u synapses:", n_plastic_synapses);
    for (uint32_t i = 0; i < n_plastic_synapses; ++i) {
        // Get next control word (auto incrementing control word)
        uint32_t control_word = *(control_words + i);
        uint32_t synapse_type = synapse_row_sparse_type(control_word, synapse_index_bits, synapse_type_mask);

        // Get state
        //const synapse_word_t data_word = *(plastic_words + i * plastic_synapse_word_stride * sizeof(synapse_word_t));
        const synapse_word_t data_word = plastic_words[i];
        synapse_state_t update_state = synapse_structure_get_update_state(data_word, synapse_type);

        const uint32_t delay = synapse_row_sparse_delay(control_word, synapse_type_index_bits, synapse_delay_mask);
        const uint32_t post_neuron_id = synapse_row_sparse_index(control_word, synapse_index_mask);

        log_info("[NESTML synapse] \t\tidx = %d\n", i);
        log_info("[NESTML synapse] \t\t  synapse_index_mask = %x\n", synapse_index_mask);
        /*log_info("[NESTML synapse] \t\t  control word = 0x%x; data word = 0x%x; synapse_type = %x; d = 0x%x, post neuron id = %u, mask = %x",
                   control_word,
                   data_word,
                   synapse_type,
                   delay,
                   post_neuron_id,
                   synapse_index_mask);*/
        log_info("[NESTML synapse] \t\t  control word = 0x%x\n", control_word);
        log_info("[NESTML synapse] \t\t  data word.w = 0x%x\n", data_word.w);
//        log_info("[NESTML synapse] \t\t  data word = 0x%x\n", data_word.post_trace);
        log_info("[NESTML synapse] \t\t  synapse_type = 0x%x\n", synapse_type);
        log_info("[NESTML synapse] \t\t  d = 0x%x\n", delay);
        log_info("[NESTML synapse] \t\t  post neuron id = %u\n", post_neuron_id);
        log_info("[NESTML synapse] \t\t  mask = %x\n", synapse_index_mask);
    }
#endif
}




//! \brief Process the dynamics of the synapses -- this function is called upon the arrival of each presynaptic spike at the synapse
//! \param[in,out] plastic_region_data: Where the plastic data is
//! \param[in] fixed_region: Where the fixed data is
//! \param[in,out] ring_buffers: The ring buffers
//! \param[in] time: The current simulation time
//! \param[out] Whether to write back anything
//! \return Whether the processing was successful or not
bool synapse_dynamics_process_plastic_synapses(
        synapse_row_plastic_data_t *plastic_region_address,
        synapse_row_fixed_part_t *fixed_region,
        weight_t *ring_buffers,
        uint32_t time,
        uint32_t colour_delay,
        bool *write_back) {

    // Extract separate arrays of plastic synapses (from plastic region),
    // Control words (from fixed region) and number of plastic synapses
    synapse_word_t *plastic_words = plastic_region_address->synapses;
    control_t *control_words = synapse_row_plastic_controls(fixed_region);
    const size_t n_plastic_synapses = synapse_row_num_plastic_controls(fixed_region);
    log_info("[NESTML synapse] synapse_dynamics_process_plastic_synapses(time = %u, n_plastic_synapses = %d)", time, n_plastic_synapses);

#ifdef PLOT_DETAILED_STATE2
    print_low_level_synaptic_row_data(plastic_region_address, fixed_region);
#endif

    num_plastic_pre_synaptic_events += n_plastic_synapses;

    // Get last pre-synaptic event from event history
    const uint32_t last_pre_time = plastic_region_address->history.prev_time;
    // update the state of presynaptic neuron-related variables common to all synapses

    const accum __h = time - last_pre_time;   // XXX: time constants are in ms, so __h should be as well! convert uint32_t to accum type
    const accum __P__pre_trace__for__stdp_synapse_nestml__pre_trace__for__stdp_synapse_nestml = expk(_kdivk((-__h), plasticity_weight_region_data->tau_tr_pre));    // type: real

    // update the state from the time of the last pre spike to the current time


//log_info("[NESTML synapse] plastic_region_address->history.pre_trace__for__stdp_synapse_nestml = %x = %k\n", plastic_region_address->history.pre_trace__for__stdp_synapse_nestml, plastic_region_address->history.pre_trace__for__stdp_synapse_nestml);
    const REAL pre_trace__for__stdp_synapse_nestml__tmp = __P__pre_trace__for__stdp_synapse_nestml__pre_trace__for__stdp_synapse_nestml * plastic_region_address->history.pre_trace__for__stdp_synapse_nestml;
    plastic_region_address->history.pre_trace__for__stdp_synapse_nestml = pre_trace__for__stdp_synapse_nestml__tmp;
    // update the state due to statements triggered by spike emission
    plastic_region_address->history.pre_trace__for__stdp_synapse_nestml += 1;
//log_info("[NESTML synapse] plastic_region_address->history.pre_trace__for__stdp_synapse_nestml = %x = %k\n", plastic_region_address->history.pre_trace__for__stdp_synapse_nestml, plastic_region_address->history.pre_trace__for__stdp_synapse_nestml);

    control_words = synapse_row_plastic_controls(fixed_region);
    plastic_words = plastic_region_address->synapses;

    // Loop through plastic synapses
    for (size_t i = 0; i < n_plastic_synapses; ++i) {
        // Get next control word (auto incrementing)
        uint32_t control_word = *(control_words + i);

//        log_info("[NESTML synapse] old plastic word[%d] = %x\n", i, plastic_words[i * plastic_synapse_word_stride]);
        process_plastic_synapse(plastic_region_address,
                                control_word,
                                last_pre_time,
                                plastic_region_address->history.pre_trace__for__stdp_synapse_nestml,
                                ring_buffers,
                                time,
                                colour_delay,
                                &plastic_words[i]);
    }

    // Update time of last pre spike in the header
    plastic_region_address->history.prev_time = time - colour_delay;

    *write_back = true;

    return true;
}


//! \brief Inform the synapses that the neuron fired
//! \param[in] time: The current simulation time
//! \param[in] neuron_index: Which neuron are we processing
void synapse_dynamics_process_post_synaptic_event(uint32_t time, index_t neuron_index) {
    log_info("[NESTML synapse] Adding post-synaptic event to buffer at time: %u, neuron_idx = %d", time, neuron_index);

    // Add post-event
    post_event_history_t *history = &post_event_history[neuron_index];
    const uint32_t last_post_time = history->times[history->count_minus_one];
    // update variables in the postsynaptic header (i.e. in the post-history-buffer)
    const accum __h = time - last_post_time;   // XXX: time constants are in ms, so __h should be as well! convert uint32_t to accum type


    const accum __P__post_trace__for__stdp_synapse_nestml__post_trace__for__stdp_synapse_nestml = expk(_kdivk((-__h), plasticity_weight_region_data->tau_tr_post));    // type: real

    // update the state from the time of the last post spike to the current time
    REAL post_trace__for__stdp_synapse_nestml__tmp = __P__post_trace__for__stdp_synapse_nestml__post_trace__for__stdp_synapse_nestml * history->post_trace__for__stdp_synapse_nestml[history->count_minus_one];




    // update the state due to statements triggered by spike emission
    post_trace__for__stdp_synapse_nestml__tmp += 1;



    // Add the post-synaptic event to the history
    uint32_t new_index;
    if (history->count_minus_one < MAX_POST_SYNAPTIC_EVENTS - 1) {
        // If there's still space, store time at current end and increment count minus 1
        new_index = ++history->count_minus_one;
    }
    else {
        // Otherwise Shuffle down elements
        // **NOTE** 1st element is always an entry at time 0
        for (uint32_t e = 2; e < MAX_POST_SYNAPTIC_EVENTS; e++) {
            history->times[e - 1] = history->times[e];
            history->post_trace__for__stdp_synapse_nestml[e - 1] = history->post_trace__for__stdp_synapse_nestml[e];
        }

        new_index = MAX_POST_SYNAPTIC_EVENTS - 1;
    }

    // write the new values back to history
    history->times[new_index] = time;
    history->post_trace__for__stdp_synapse_nestml[new_index] = post_trace__for__stdp_synapse_nestml__tmp;
}



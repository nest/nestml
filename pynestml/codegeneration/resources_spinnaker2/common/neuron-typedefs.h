#ifndef __NEURON_TYPEDEFS_H__
#define __NEURON_TYPEDEFS_H__

#include <common-typedefs.h>
#include "maths-util.h"

#ifndef __SPIKE_T__

typedef uint32_t payload_t;

#ifdef SPIKES_WITH_PAYLOADS

typedef uint64_t spike_t;

static inline payload_t spike_payload (spike_t s) {
    return ((payload_t)(s & UINT32_MAX));
}

#else  

typedef uint32_t spike_t;


static inline payload_t spike_payload(spike_t s) {
    use(s);
    return (0);
}
#endif 
#endif 

typedef address_t synaptic_row_t;

typedef REAL input_t;

typedef struct input_struct_t{
    input_t exc;
    input_t inh;
} input_struct_t;

typedef struct timed_input_t {
    uint32_t time;
    input_struct_t inputs[];
} timed_input_t;

typedef float state_t;

typedef struct timed_state_t {
    uint32_t time;
    state_t states[];
} timed_state_t;


#endif /* __NEURON_TYPEDEFS_H__ */

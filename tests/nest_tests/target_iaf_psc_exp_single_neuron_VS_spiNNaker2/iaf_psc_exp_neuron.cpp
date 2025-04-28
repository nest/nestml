
/*
 *  iaf_psc_exp_neuron.cpp
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
 *  Generated from NESTML 8.0.0-post-dev at time: 2025-03-27 09:34:04.165725
**/

// C++ includes:
#include <limits>

// Includes from libnestutil:
#include "numerics.h"

// Includes from nestkernel:
#include "exceptions.h"
#include "kernel_manager.h"
#include "nest_impl.h"
#include "universal_data_logger_impl.h"

// Includes from sli:
#include "dict.h"
#include "dictutils.h"
#include "doubledatum.h"
#include "integerdatum.h"
#include "lockptrdatum.h"

#include "iaf_psc_exp_neuron.h"

// uncomment the next line to enable printing of detailed debug information
// #define DEBUG
void
register_iaf_psc_exp_neuron( const std::string& name )
{
  nest::register_node_model< iaf_psc_exp_neuron >( name );
}

// ---------------------------------------------------------------------------
//   Recordables map
// ---------------------------------------------------------------------------
nest::RecordablesMap<iaf_psc_exp_neuron> iaf_psc_exp_neuron::recordablesMap_;
namespace nest
{

  // Override the create() method with one call to RecordablesMap::insert_()
  // for each quantity to be recorded.
template <> void RecordablesMap<iaf_psc_exp_neuron>::create()
  {
    // add state variables to recordables map
   insert_(iaf_psc_exp_neuron_names::_V_m, &iaf_psc_exp_neuron::get_V_m);
   insert_(iaf_psc_exp_neuron_names::_refr_t, &iaf_psc_exp_neuron::get_refr_t);
   insert_(iaf_psc_exp_neuron_names::_I_syn_exc, &iaf_psc_exp_neuron::get_I_syn_exc);
   insert_(iaf_psc_exp_neuron_names::_I_syn_inh, &iaf_psc_exp_neuron::get_I_syn_inh);

    // Add vector variables  
  }
}
std::vector< std::tuple< int, int > > iaf_psc_exp_neuron::rport_to_nestml_buffer_idx =
{
  
  { iaf_psc_exp_neuron::EXC_SPIKES, iaf_psc_exp_neuron::INH_SPIKES },
};

// ---------------------------------------------------------------------------
//   Default constructors defining default parameters and state
//   Note: the implementation is empty. The initialization is of variables
//   is a part of iaf_psc_exp_neuron's constructor.
// ---------------------------------------------------------------------------

iaf_psc_exp_neuron::Parameters_::Parameters_()
{
}

iaf_psc_exp_neuron::State_::State_()
{
}

// ---------------------------------------------------------------------------
//   Parameter and state extractions and manipulation functions
// ---------------------------------------------------------------------------

iaf_psc_exp_neuron::Buffers_::Buffers_(iaf_psc_exp_neuron &n):
  logger_(n)
  , spike_inputs_( std::vector< nest::RingBuffer >( NUM_SPIKE_RECEPTORS ) )
  , spike_inputs_grid_sum_( std::vector< double >( NUM_SPIKE_RECEPTORS ) )
  , spike_input_received_( std::vector< nest::RingBuffer >( NUM_SPIKE_RECEPTORS ) )
  , spike_input_received_grid_sum_( std::vector< double >( NUM_SPIKE_RECEPTORS ) )
{
  // Initialization of the remaining members is deferred to init_buffers_().
}

iaf_psc_exp_neuron::Buffers_::Buffers_(const Buffers_ &, iaf_psc_exp_neuron &n):
  logger_(n)
  , spike_inputs_( std::vector< nest::RingBuffer >( NUM_SPIKE_RECEPTORS ) )
  , spike_inputs_grid_sum_( std::vector< double >( NUM_SPIKE_RECEPTORS ) )
  , spike_input_received_( std::vector< nest::RingBuffer >( NUM_SPIKE_RECEPTORS ) )
  , spike_input_received_grid_sum_( std::vector< double >( NUM_SPIKE_RECEPTORS ) )
{
  // Initialization of the remaining members is deferred to init_buffers_().
}

// ---------------------------------------------------------------------------
//   Default constructor for node
// ---------------------------------------------------------------------------

iaf_psc_exp_neuron::iaf_psc_exp_neuron():ArchivingNode(), P_(), S_(), B_(*this)
{
  init_state_internal_();
  recordablesMap_.create();
  pre_run_hook();
}

// ---------------------------------------------------------------------------
//   Copy constructor for node
// ---------------------------------------------------------------------------

iaf_psc_exp_neuron::iaf_psc_exp_neuron(const iaf_psc_exp_neuron& __n):
  ArchivingNode(), P_(__n.P_), S_(__n.S_), B_(__n.B_, *this)
{
  // copy parameter struct P_
  P_.C_m = __n.P_.C_m;
  P_.tau_m = __n.P_.tau_m;
  P_.tau_syn_inh = __n.P_.tau_syn_inh;
  P_.tau_syn_exc = __n.P_.tau_syn_exc;
  P_.refr_T = __n.P_.refr_T;
  P_.E_L = __n.P_.E_L;
  P_.V_reset = __n.P_.V_reset;
  P_.V_th = __n.P_.V_th;
  P_.I_e = __n.P_.I_e;

  // copy state struct S_
  S_.V_m = __n.S_.V_m;
  S_.refr_t = __n.S_.refr_t;
  S_.I_syn_exc = __n.S_.I_syn_exc;
  S_.I_syn_inh = __n.S_.I_syn_inh;

  // copy internals V_
  V_.__h = __n.V_.__h;
  V_.__P__I_syn_exc__I_syn_exc = __n.V_.__P__I_syn_exc__I_syn_exc;
  V_.__P__I_syn_inh__I_syn_inh = __n.V_.__P__I_syn_inh__I_syn_inh;
  V_.__P__V_m__I_syn_exc = __n.V_.__P__V_m__I_syn_exc;
  V_.__P__V_m__I_syn_inh = __n.V_.__P__V_m__I_syn_inh;
  V_.__P__V_m__V_m = __n.V_.__P__V_m__V_m;
  V_.__P__refr_t__refr_t = __n.V_.__P__refr_t__refr_t;
}

// ---------------------------------------------------------------------------
//   Destructor for node
// ---------------------------------------------------------------------------

iaf_psc_exp_neuron::~iaf_psc_exp_neuron()
{
}

// ---------------------------------------------------------------------------
//   Node initialization functions
// ---------------------------------------------------------------------------
void iaf_psc_exp_neuron::calibrate_time( const nest::TimeConverter& tc )
{
  LOG( nest::M_WARNING,
    "iaf_psc_exp_neuron",
    "Simulation resolution has changed. Internal state and parameters of the model have been reset!" );

  init_state_internal_();
}
void iaf_psc_exp_neuron::init_state_internal_()
{
#ifdef DEBUG
  std::cout << "[neuron " << this << "] iaf_psc_exp_neuron::init_state_internal_()" << std::endl;
#endif

  const double __timestep = nest::Time::get_resolution().get_ms();  // do not remove, this is necessary for the timestep() function
  // initial values for parameters
  P_.C_m = 250; // as pF
  P_.tau_m = 10; // as ms
  P_.tau_syn_inh = 2; // as ms
  P_.tau_syn_exc = 2; // as ms
  P_.refr_T = 2; // as ms
  P_.E_L = (-70); // as mV
  P_.V_reset = (-70); // as mV
  P_.V_th = (-55); // as mV
  P_.I_e = 0; // as pA

  V_.__h = nest::Time::get_resolution().get_ms();
  recompute_internal_variables();
  // initial values for state variables
  S_.V_m = P_.E_L; // as mV
  S_.refr_t = 0; // as ms
  S_.I_syn_exc = 0; // as pA
  S_.I_syn_inh = 0; // as pA
}

void iaf_psc_exp_neuron::init_buffers_()
{
#ifdef DEBUG
  std::cout << "[neuron " << this << "] iaf_psc_exp_neuron::init_buffers_()" << std::endl;
#endif
  // spike input buffers
  get_spike_inputs_().clear();
  get_spike_inputs_grid_sum_().clear();
  get_spike_input_received_().clear();
  get_spike_input_received_grid_sum_().clear();


  // continuous time input buffers  

  get_I_stim().clear();
  B_.I_stim_grid_sum_ = 0;

  B_.logger_.reset();


}

void iaf_psc_exp_neuron::recompute_internal_variables(bool exclude_timestep)
{
  const double __timestep = nest::Time::get_resolution().get_ms();  // do not remove, this is necessary for the timestep() function

  if (exclude_timestep)
  {    
    V_.__P__I_syn_exc__I_syn_exc = std::exp((-V_.__h) / P_.tau_syn_exc); // as real
    V_.__P__I_syn_inh__I_syn_inh = std::exp((-V_.__h) / P_.tau_syn_inh); // as real
    V_.__P__V_m__I_syn_exc = P_.tau_m * P_.tau_syn_exc * ((-std::exp(V_.__h / P_.tau_m)) + std::exp(V_.__h / P_.tau_syn_exc)) * std::exp((-V_.__h) * (P_.tau_m + P_.tau_syn_exc) / (P_.tau_m * P_.tau_syn_exc)) / (P_.C_m * (P_.tau_m - P_.tau_syn_exc)); // as real
    V_.__P__V_m__I_syn_inh = P_.tau_m * P_.tau_syn_inh * (std::exp(V_.__h / P_.tau_m) - std::exp(V_.__h / P_.tau_syn_inh)) * std::exp((-V_.__h) * (P_.tau_m + P_.tau_syn_inh) / (P_.tau_m * P_.tau_syn_inh)) / (P_.C_m * (P_.tau_m - P_.tau_syn_inh)); // as real
    V_.__P__V_m__V_m = std::exp((-V_.__h) / P_.tau_m); // as real
    V_.__P__refr_t__refr_t = 1; // as real
  }
  else {    
    V_.__h = nest::Time::get_resolution().get_ms(); // as ms
    V_.__P__I_syn_exc__I_syn_exc = std::exp((-V_.__h) / P_.tau_syn_exc); // as real
    V_.__P__I_syn_inh__I_syn_inh = std::exp((-V_.__h) / P_.tau_syn_inh); // as real
    V_.__P__V_m__I_syn_exc = P_.tau_m * P_.tau_syn_exc * ((-std::exp(V_.__h / P_.tau_m)) + std::exp(V_.__h / P_.tau_syn_exc)) * std::exp((-V_.__h) * (P_.tau_m + P_.tau_syn_exc) / (P_.tau_m * P_.tau_syn_exc)) / (P_.C_m * (P_.tau_m - P_.tau_syn_exc)); // as real
    V_.__P__V_m__I_syn_inh = P_.tau_m * P_.tau_syn_inh * (std::exp(V_.__h / P_.tau_m) - std::exp(V_.__h / P_.tau_syn_inh)) * std::exp((-V_.__h) * (P_.tau_m + P_.tau_syn_inh) / (P_.tau_m * P_.tau_syn_inh)) / (P_.C_m * (P_.tau_m - P_.tau_syn_inh)); // as real
    V_.__P__V_m__V_m = std::exp((-V_.__h) / P_.tau_m); // as real
    V_.__P__refr_t__refr_t = 1; // as real
  }
}
void iaf_psc_exp_neuron::pre_run_hook()
{
#ifdef DEBUG
  std::cout << "[neuron " << this << "] iaf_psc_exp_neuron::pre_run_hook()" << std::endl;
#endif

  B_.logger_.init();

  // parameters might have changed -- recompute internals
  V_.__h = nest::Time::get_resolution().get_ms();
  recompute_internal_variables();

  // buffers B_
  B_.spike_inputs_.resize(NUM_SPIKE_RECEPTORS);
  B_.spike_inputs_grid_sum_.resize(NUM_SPIKE_RECEPTORS);
  B_.spike_input_received_.resize(NUM_SPIKE_RECEPTORS);
  B_.spike_input_received_grid_sum_.resize(NUM_SPIKE_RECEPTORS);
}

// ---------------------------------------------------------------------------
//   Update and spike handling functions
// ---------------------------------------------------------------------------


void iaf_psc_exp_neuron::update(nest::Time const & origin, const long from, const long to)
{
  const double __timestep = nest::Time::get_resolution().get_ms();  // do not remove, this is necessary for the timestep() function

  for ( long lag = from ; lag < to ; ++lag )
  {


    auto get_t = [origin, lag](){ return nest::Time( nest::Time::step( origin.get_steps() + lag + 1) ).get_ms(); };

#ifdef DEBUG
    std::cout << "[neuron " << this << "] iaf_psc_exp_neuron::update: handling post spike at t = " << get_t() << std::endl;
#endif
    /**
     * buffer spikes from spiking input ports
    **/

    for (long i = 0; i < NUM_SPIKE_RECEPTORS; ++i)
    {
      get_spike_inputs_grid_sum_()[i] = get_spike_inputs_()[i].get_value(lag);
      get_spike_input_received_grid_sum_()[i] = get_spike_input_received_()[i].get_value(lag);
    }

    /**
     * subthreshold updates of the convolution variables
     *
     * step 1: regardless of whether and how integrate_odes() will be called, update variables due to convolutions
    **/



    /**
     * Begin NESTML generated code for the update block(s)
    **/

  if (S_.refr_t > 0)
  {  

    // start rendered code for integrate_odes(I_syn_exc, I_syn_inh, refr_t)

    // analytic solver: integrating state variables (first step): I_syn_exc, I_syn_inh, refr_t, 
    const double I_syn_exc__tmp = S_.I_syn_exc * V_.__P__I_syn_exc__I_syn_exc;
    const double I_syn_inh__tmp = S_.I_syn_inh * V_.__P__I_syn_inh__I_syn_inh;
    const double refr_t__tmp = V_.__P__refr_t__refr_t * S_.refr_t - 1.0 * V_.__h;
    // analytic solver: integrating state variables (second step): I_syn_exc, I_syn_inh, refr_t, 
    /* replace analytically solvable variables with precisely integrated values  */
    S_.I_syn_exc = I_syn_exc__tmp;
    S_.I_syn_inh = I_syn_inh__tmp;
    S_.refr_t = refr_t__tmp;
  }
  else
  {  

    // start rendered code for integrate_odes(I_syn_exc, I_syn_inh, V_m)

    // analytic solver: integrating state variables (first step): I_syn_exc, I_syn_inh, V_m, 
    const double I_syn_exc__tmp = S_.I_syn_exc * V_.__P__I_syn_exc__I_syn_exc;
    const double I_syn_inh__tmp = S_.I_syn_inh * V_.__P__I_syn_inh__I_syn_inh;
    const double V_m__tmp = (-P_.E_L) * V_.__P__V_m__V_m + P_.E_L + S_.I_syn_exc * V_.__P__V_m__I_syn_exc + S_.I_syn_inh * V_.__P__V_m__I_syn_inh + S_.V_m * V_.__P__V_m__V_m - P_.I_e * V_.__P__V_m__V_m * P_.tau_m / P_.C_m + P_.I_e * P_.tau_m / P_.C_m - B_.I_stim_grid_sum_ * V_.__P__V_m__V_m * P_.tau_m / P_.C_m + B_.I_stim_grid_sum_ * P_.tau_m / P_.C_m;
    // analytic solver: integrating state variables (second step): I_syn_exc, I_syn_inh, V_m, 
    /* replace analytically solvable variables with precisely integrated values  */
    S_.I_syn_exc = I_syn_exc__tmp;
    S_.I_syn_inh = I_syn_inh__tmp;
    S_.V_m = V_m__tmp;
  }

    /**
     * Begin NESTML generated code for the onReceive block(s)
    **/

    if (B_.spike_input_received_grid_sum_[EXC_SPIKES - MIN_SPIKE_RECEPTOR])
    {
      // B_.spike_input_received_[EXC_SPIKES - MIN_SPIKE_RECEPTOR] = false;  // no need to reset the flag -- reading from the RingBuffer into the "grid_sum" variables resets the RingBuffer entries
      on_receive_block_exc_spikes();
    }
    if (B_.spike_input_received_grid_sum_[INH_SPIKES - MIN_SPIKE_RECEPTOR])
    {
      // B_.spike_input_received_[INH_SPIKES - MIN_SPIKE_RECEPTOR] = false;  // no need to reset the flag -- reading from the RingBuffer into the "grid_sum" variables resets the RingBuffer entries
      on_receive_block_inh_spikes();
    }

    /**
     * subthreshold updates of the convolution variables
     *
     * step 2: regardless of whether and how integrate_odes() was called, update variables due to convolutions. Set to the updated values at the end of the timestep.
    **/


    /**
     * spike updates due to convolutions
    **/


    /**
     * Begin NESTML generated code for the onCondition block(s)
    **/

    if (S_.refr_t <= 0 && S_.V_m >= P_.V_th)
    {
      S_.refr_t = P_.refr_T;
      S_.V_m = P_.V_reset;

      // begin generated code for emit_spike() function

      #ifdef DEBUG
      std::cout << "Emitting a spike at t = " << nest::Time(nest::Time::step(origin.get_steps() + lag + 1)).get_ms() << "\n";
      #endif
      set_spiketime(nest::Time::step(origin.get_steps() + lag + 1));
      nest::SpikeEvent se;
      nest::kernel().event_delivery_manager.send(*this, se, lag);
      // end generated code for emit_spike() function
    }

    /**
     * handle continuous input ports
    **/

    B_.I_stim_grid_sum_ = get_I_stim().get_value(lag);
    // voltage logging
    B_.logger_.record_data(origin.get_steps() + lag);
  }
}

// Do not move this function as inline to h-file. It depends on
// universal_data_logger_impl.h being included here.
void iaf_psc_exp_neuron::handle(nest::DataLoggingRequest& e)
{
  B_.logger_.handle(e);
}


void iaf_psc_exp_neuron::handle(nest::SpikeEvent &e)
{
#ifdef DEBUG
  std::cout << "[neuron " << this << "] iaf_psc_exp_neuron::handle(SpikeEvent)" << std::endl;
#endif

  assert(e.get_delay_steps() > 0);
  assert( e.get_rport() < B_.spike_inputs_.size() );

  double weight = e.get_weight();
  size_t nestml_buffer_idx = 0;
  if ( weight >= 0.0 )
  {
    nestml_buffer_idx = std::get<0>(rport_to_nestml_buffer_idx[e.get_rport()]);
  }
  else
  {
    nestml_buffer_idx = std::get<1>(rport_to_nestml_buffer_idx[e.get_rport()]);
    if ( nestml_buffer_idx == iaf_psc_exp_neuron::PORT_NOT_AVAILABLE )
    {
      nestml_buffer_idx = std::get<0>(rport_to_nestml_buffer_idx[e.get_rport()]);
    }
    weight = -weight;
  }
  B_.spike_inputs_[ nestml_buffer_idx - MIN_SPIKE_RECEPTOR ].add_value(
    e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin() ),
    weight * e.get_multiplicity() );
  B_.spike_input_received_[ nestml_buffer_idx - MIN_SPIKE_RECEPTOR ].add_value(
    e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin() ),
    1. );
}

void iaf_psc_exp_neuron::handle(nest::CurrentEvent& e)
{
#ifdef DEBUG
  std::cout << "[neuron " << this << "] iaf_psc_exp_neuron::handle(CurrentEvent)" << std::endl;
#endif
  assert(e.get_delay_steps() > 0);

  const double current = e.get_current();     // we assume that in NEST, this returns a current in pA
  const double weight = e.get_weight();
  get_I_stim().add_value(
               e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin()),
               weight * current );
}

// -------------------------------------------------------------------------
//   Methods corresponding to event handlers
// -------------------------------------------------------------------------
void
iaf_psc_exp_neuron::on_receive_block_exc_spikes()
{
  const double __timestep = nest::Time::get_resolution().get_ms();  // do not remove, this is necessary for the timestep() function  
  S_.I_syn_exc += (0.001 * B_.spike_inputs_grid_sum_[EXC_SPIKES - MIN_SPIKE_RECEPTOR]) * 1.0 * 1000.0;
}


void
iaf_psc_exp_neuron::on_receive_block_inh_spikes()
{
  const double __timestep = nest::Time::get_resolution().get_ms();  // do not remove, this is necessary for the timestep() function  
  S_.I_syn_inh += (0.001 * B_.spike_inputs_grid_sum_[INH_SPIKES - MIN_SPIKE_RECEPTOR]) * 1.0 * 1000.0;
}




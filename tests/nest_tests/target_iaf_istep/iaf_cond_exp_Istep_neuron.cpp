
/*
 *  iaf_cond_exp_Istep_neuron.cpp
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
 *  Generated from NESTML 8.0.0-post-dev at time: 2025-03-18 10:09:29.438700
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

#include "iaf_cond_exp_Istep_neuron.h"

// uncomment the next line to enable printing of detailed debug information
// #define DEBUG
void
register_iaf_cond_exp_Istep_neuron( const std::string& name )
{
  nest::register_node_model< iaf_cond_exp_Istep_neuron >( name );
}

// ---------------------------------------------------------------------------
//   Recordables map
// ---------------------------------------------------------------------------
nest::RecordablesMap<iaf_cond_exp_Istep_neuron> iaf_cond_exp_Istep_neuron::recordablesMap_;
namespace nest
{

  // Override the create() method with one call to RecordablesMap::insert_()
  // for each quantity to be recorded.
template <> void RecordablesMap<iaf_cond_exp_Istep_neuron>::create()
  {
    // add state variables to recordables map
   insert_(iaf_cond_exp_Istep_neuron_names::_V_m, &iaf_cond_exp_Istep_neuron::get_V_m);
   insert_(iaf_cond_exp_Istep_neuron_names::_refr_t, &iaf_cond_exp_Istep_neuron::get_refr_t);
   insert_(iaf_cond_exp_Istep_neuron_names::_I_step_now, &iaf_cond_exp_Istep_neuron::get_I_step_now);
   insert_(iaf_cond_exp_Istep_neuron_names::_g_ex__X__exc_spikes, &iaf_cond_exp_Istep_neuron::get_g_ex__X__exc_spikes);
   insert_(iaf_cond_exp_Istep_neuron_names::_g_in__X__inh_spikes, &iaf_cond_exp_Istep_neuron::get_g_in__X__inh_spikes);

    // Add vector variables  
  }
}
std::vector< std::tuple< int, int > > iaf_cond_exp_Istep_neuron::rport_to_nestml_buffer_idx =
{
  
  { iaf_cond_exp_Istep_neuron::EXC_SPIKES, iaf_cond_exp_Istep_neuron::INH_SPIKES },
};

// ---------------------------------------------------------------------------
//   Default constructors defining default parameters and state
//   Note: the implementation is empty. The initialization is of variables
//   is a part of iaf_cond_exp_Istep_neuron's constructor.
// ---------------------------------------------------------------------------

iaf_cond_exp_Istep_neuron::Parameters_::Parameters_()
{
}

iaf_cond_exp_Istep_neuron::State_::State_()
{
}

// ---------------------------------------------------------------------------
//   Parameter and state extractions and manipulation functions
// ---------------------------------------------------------------------------

iaf_cond_exp_Istep_neuron::Buffers_::Buffers_(iaf_cond_exp_Istep_neuron &n):
  logger_(n)
  , spike_inputs_( std::vector< nest::RingBuffer >( NUM_SPIKE_RECEPTORS ) )
  , spike_inputs_grid_sum_( std::vector< double >( NUM_SPIKE_RECEPTORS ) )
  , spike_input_received_( std::vector< nest::RingBuffer >( NUM_SPIKE_RECEPTORS ) )
  , spike_input_received_grid_sum_( std::vector< double >( NUM_SPIKE_RECEPTORS ) )
  , __s( nullptr ), __c( nullptr ), __e( nullptr )
{
  // Initialization of the remaining members is deferred to init_buffers_().
}

iaf_cond_exp_Istep_neuron::Buffers_::Buffers_(const Buffers_ &, iaf_cond_exp_Istep_neuron &n):
  logger_(n)
  , spike_inputs_( std::vector< nest::RingBuffer >( NUM_SPIKE_RECEPTORS ) )
  , spike_inputs_grid_sum_( std::vector< double >( NUM_SPIKE_RECEPTORS ) )
  , spike_input_received_( std::vector< nest::RingBuffer >( NUM_SPIKE_RECEPTORS ) )
  , spike_input_received_grid_sum_( std::vector< double >( NUM_SPIKE_RECEPTORS ) )
  , __s( nullptr ), __c( nullptr ), __e( nullptr )
{
  // Initialization of the remaining members is deferred to init_buffers_().
}

// ---------------------------------------------------------------------------
//   Default constructor for node
// ---------------------------------------------------------------------------

iaf_cond_exp_Istep_neuron::iaf_cond_exp_Istep_neuron():ArchivingNode(), P_(), S_(), B_(*this)
{
  init_state_internal_();
  recordablesMap_.create();
  pre_run_hook();
}

// ---------------------------------------------------------------------------
//   Copy constructor for node
// ---------------------------------------------------------------------------

iaf_cond_exp_Istep_neuron::iaf_cond_exp_Istep_neuron(const iaf_cond_exp_Istep_neuron& __n):
  ArchivingNode(), P_(__n.P_), S_(__n.S_), B_(__n.B_, *this)
{
  // copy parameter struct P_
  P_.V_th = __n.P_.V_th;
  P_.V_reset = __n.P_.V_reset;
  P_.refr_T = __n.P_.refr_T;
  P_.g_L = __n.P_.g_L;
  P_.C_m = __n.P_.C_m;
  P_.E_ex = __n.P_.E_ex;
  P_.E_in = __n.P_.E_in;
  P_.E_L = __n.P_.E_L;
  P_.tau_syn_ex = __n.P_.tau_syn_ex;
  P_.tau_syn_in = __n.P_.tau_syn_in;
  P_.I_e = __n.P_.I_e;
  P_.n_step = __n.P_.n_step;
  P_.I_step = __n.P_.I_step;
  P_.t_step = __n.P_.t_step;

  // copy state struct S_
  S_.ode_state[State_::V_m] = __n.S_.ode_state[State_::V_m];
  S_.refr_t = __n.S_.refr_t;
  S_.is_refractory = __n.S_.is_refractory;
  S_.k_step = __n.S_.k_step;
  S_.I_step_now = __n.S_.I_step_now;
  S_.ode_state[State_::g_ex__X__exc_spikes] = __n.S_.ode_state[State_::g_ex__X__exc_spikes];
  S_.ode_state[State_::g_in__X__inh_spikes] = __n.S_.ode_state[State_::g_in__X__inh_spikes];

  // copy internals V_
  V_.__h = __n.V_.__h;
  V_.__P__g_ex__X__exc_spikes__g_ex__X__exc_spikes = __n.V_.__P__g_ex__X__exc_spikes__g_ex__X__exc_spikes;
  V_.__P__g_in__X__inh_spikes__g_in__X__inh_spikes = __n.V_.__P__g_in__X__inh_spikes__g_in__X__inh_spikes;
}

// ---------------------------------------------------------------------------
//   Destructor for node
// ---------------------------------------------------------------------------

iaf_cond_exp_Istep_neuron::~iaf_cond_exp_Istep_neuron()
{
  // GSL structs may not have been allocated, so we need to protect destruction

  if (B_.__s)
  {
    gsl_odeiv_step_free( B_.__s );
  }

  if (B_.__c)
  {
    gsl_odeiv_control_free( B_.__c );
  }

  if (B_.__e)
  {
    gsl_odeiv_evolve_free( B_.__e );
  }
}

// ---------------------------------------------------------------------------
//   Node initialization functions
// ---------------------------------------------------------------------------
void iaf_cond_exp_Istep_neuron::calibrate_time( const nest::TimeConverter& tc )
{
  LOG( nest::M_WARNING,
    "iaf_cond_exp_Istep_neuron",
    "Simulation resolution has changed. Internal state and parameters of the model have been reset!" );

  init_state_internal_();
}
void iaf_cond_exp_Istep_neuron::init_state_internal_()
{
#ifdef DEBUG
  std::cout << "[neuron " << this << "] iaf_cond_exp_Istep_neuron::init_state_internal_()" << std::endl;
#endif

  const double __timestep = nest::Time::get_resolution().get_ms();  // do not remove, this is necessary for the timestep() function
  // by default, integrate all variables with a conservative tolerance, in the sense that we err on the side of integrating very precisely at the expense of extra computation
  P_.__gsl_abs_error_tol = 1e-6;
  P_.__gsl_rel_error_tol = 1e-6;
  // initial values for parameters
  P_.V_th = (-55); // as mV
  P_.V_reset = (-60); // as mV
  P_.refr_T = 2; // as ms
  P_.g_L = 16.6667; // as nS
  P_.C_m = 250; // as pF
  P_.E_ex = 0; // as mV
  P_.E_in = (-85); // as mV
  P_.E_L = (-70); // as mV
  P_.tau_syn_ex = 0.2; // as ms
  P_.tau_syn_in = 2; // as ms
  P_.I_e = 0; // as pA
  P_.n_step = 1; // as integer
  P_.I_step.resize(
  P_.n_step, 0.0);
  P_.t_step.resize(
  P_.n_step, 0.0);

  V_.__h = nest::Time::get_resolution().get_ms();
  recompute_internal_variables();
  // initial values for state variables
  S_.ode_state[State_::V_m] = P_.E_L; // as mV
  S_.refr_t = 0; // as ms
  S_.is_refractory = false; // as boolean
  S_.k_step = 0; // as integer
  S_.I_step_now = 0.0; // as pA
  S_.ode_state[State_::g_ex__X__exc_spikes] = 0; // as real
  S_.ode_state[State_::g_in__X__inh_spikes] = 0; // as real
}

void iaf_cond_exp_Istep_neuron::init_buffers_()
{
#ifdef DEBUG
  std::cout << "[neuron " << this << "] iaf_cond_exp_Istep_neuron::init_buffers_()" << std::endl;
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



  if ( not B_.__s )
  {
    B_.__s = gsl_odeiv_step_alloc( gsl_odeiv_step_rkf45, State_::STATE_VEC_SIZE );
  }
  else
  {
    gsl_odeiv_step_reset( B_.__s );
  }

  if ( not B_.__c )
  {
    B_.__c = gsl_odeiv_control_y_new( P_.__gsl_abs_error_tol, P_.__gsl_rel_error_tol );
  }
  else
  {
    gsl_odeiv_control_init( B_.__c, P_.__gsl_abs_error_tol, P_.__gsl_rel_error_tol, 1.0, 0.0 );

  }

  if ( not B_.__e )
  {
    B_.__e = gsl_odeiv_evolve_alloc( State_::STATE_VEC_SIZE );
  }
  else
  {
    gsl_odeiv_evolve_reset( B_.__e );
  }

  // B_.__sys.function = iaf_cond_exp_Istep_neuron_dynamics; // will be set just prior to the call to gsl_odeiv_evolve_apply()
  B_.__sys.jacobian = nullptr;
  B_.__sys.dimension = State_::STATE_VEC_SIZE;
  B_.__sys.params = reinterpret_cast< void* >( this );
  B_.__step = nest::Time::get_resolution().get_ms();
  B_.__integration_step = nest::Time::get_resolution().get_ms();
}

void iaf_cond_exp_Istep_neuron::recompute_internal_variables(bool exclude_timestep)
{
  const double __timestep = nest::Time::get_resolution().get_ms();  // do not remove, this is necessary for the timestep() function

  if (exclude_timestep)
  {    
    V_.__P__g_ex__X__exc_spikes__g_ex__X__exc_spikes = std::exp((-V_.__h) / P_.tau_syn_ex); // as real
    V_.__P__g_in__X__inh_spikes__g_in__X__inh_spikes = std::exp((-V_.__h) / P_.tau_syn_in); // as real
  }
  else {    
    V_.__h = nest::Time::get_resolution().get_ms(); // as ms
    V_.__P__g_ex__X__exc_spikes__g_ex__X__exc_spikes = std::exp((-V_.__h) / P_.tau_syn_ex); // as real
    V_.__P__g_in__X__inh_spikes__g_in__X__inh_spikes = std::exp((-V_.__h) / P_.tau_syn_in); // as real
  }
}
void iaf_cond_exp_Istep_neuron::pre_run_hook()
{
#ifdef DEBUG
  std::cout << "[neuron " << this << "] iaf_cond_exp_Istep_neuron::pre_run_hook()" << std::endl;
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

extern "C" inline int iaf_cond_exp_Istep_neuron_dynamics(double __time, const double ode_state[], double f[], void* pnode)
{
  typedef iaf_cond_exp_Istep_neuron::State_ State_;
  // get access to node so we can almost work as in a member function
  assert( pnode );
  const iaf_cond_exp_Istep_neuron& node = *( reinterpret_cast< iaf_cond_exp_Istep_neuron* >( pnode ) );

  // ode_state[] here is---and must be---the state vector supplied by the integrator,
  // not the state vector in the node, node.S_.ode_state[].


  f[State_::V_m] = (node.P_.I_e + node.S_.I_step_now + node.B_.I_stim_grid_sum_ - node.P_.g_L * ((-node.P_.E_L) + ode_state[State_::V_m]) - 1.0 * ode_state[State_::g_ex__X__exc_spikes] * ((-node.P_.E_ex) + ode_state[State_::V_m]) - 1.0 * ode_state[State_::g_in__X__inh_spikes] * ((-node.P_.E_in) + ode_state[State_::V_m])) / node.P_.C_m;
  f[State_::g_ex__X__exc_spikes] = (-ode_state[State_::g_ex__X__exc_spikes]) / node.P_.tau_syn_ex;
  f[State_::g_in__X__inh_spikes] = (-ode_state[State_::g_in__X__inh_spikes]) / node.P_.tau_syn_in;
  return GSL_SUCCESS;
}
void iaf_cond_exp_Istep_neuron::update(nest::Time const & origin, const long from, const long to)
{
  const double __timestep = nest::Time::get_resolution().get_ms();  // do not remove, this is necessary for the timestep() function

  for ( long lag = from ; lag < to ; ++lag )
  {


    auto get_t = [origin, lag](){ return nest::Time( nest::Time::step( origin.get_steps() + lag + 1) ).get_ms(); };

#ifdef DEBUG
    std::cout << "[neuron " << this << "] iaf_cond_exp_Istep_neuron::update: handling post spike at t = " << get_t() << std::endl;
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

    const double g_ex__X__exc_spikes__tmp_ = V_.__P__g_ex__X__exc_spikes__g_ex__X__exc_spikes * S_.ode_state[State_::g_ex__X__exc_spikes];
    const double g_in__X__inh_spikes__tmp_ = V_.__P__g_in__X__inh_spikes__g_in__X__inh_spikes * S_.ode_state[State_::g_in__X__inh_spikes];


    /**
     * Begin NESTML generated code for the update block(s)
    **/

  if (S_.is_refractory)
  {  
    S_.refr_t -= nest::Time::get_resolution().get_ms();
  }
  else
  {  

    // start rendered code for integrate_odes()

    // analytic solver: integrating state variables (first step): g_ex__X__exc_spikes, g_in__X__inh_spikes, 
    const double g_ex__X__exc_spikes__tmp = V_.__P__g_ex__X__exc_spikes__g_ex__X__exc_spikes * S_.ode_state[State_::g_ex__X__exc_spikes];
    const double g_in__X__inh_spikes__tmp = V_.__P__g_in__X__inh_spikes__g_in__X__inh_spikes * S_.ode_state[State_::g_in__X__inh_spikes];


    // numeric solver: integrating state variables: V_m, g_ex__X__exc_spikes, g_in__X__inh_spikes, 
    double __t = 0;
    B_.__sys.function = iaf_cond_exp_Istep_neuron_dynamics;
    // numerical integration with adaptive step size control:
    // ------------------------------------------------------
    // gsl_odeiv_evolve_apply performs only a single numerical
    // integration step, starting from t and bounded by step;
    // the while-loop ensures integration over the whole simulation
    // step (0, step] if more than one integration step is needed due
    // to a small integration step size;
    // note that (t+IntegrationStep > step) leads to integration over
    // (t, step] and afterwards setting t to step, but it does not
    // enforce setting IntegrationStep to step-t; this is of advantage
    // for a consistent and efficient integration across subsequent
    // simulation intervals
    while ( __t < B_.__step )
    {

      const int status = gsl_odeiv_evolve_apply(B_.__e,
                                                B_.__c,
                                                B_.__s,
                                                &B_.__sys,              // system of ODE
                                                &__t,                   // from t
                                                B_.__step,              // to t <= step
                                                &B_.__integration_step, // integration step size
                                                S_.ode_state);          // neuronal state

      if ( status != GSL_SUCCESS )
      {
        throw nest::GSLSolverFailure( get_name(), status );
      }
    }
    // analytic solver: integrating state variables (second step): g_ex__X__exc_spikes, g_in__X__inh_spikes, 
    /* replace analytically solvable variables with precisely integrated values  */
    S_.ode_state[State_::g_ex__X__exc_spikes] = g_ex__X__exc_spikes__tmp;
    S_.ode_state[State_::g_in__X__inh_spikes] = g_in__X__inh_spikes__tmp;
  }

    /**
     * Begin NESTML generated code for the onReceive block(s)
    **/


    /**
     * subthreshold updates of the convolution variables
     *
     * step 2: regardless of whether and how integrate_odes() was called, update variables due to convolutions. Set to the updated values at the end of the timestep.
    **/

    S_.ode_state[State_::g_ex__X__exc_spikes] = g_ex__X__exc_spikes__tmp_;
    S_.ode_state[State_::g_in__X__inh_spikes] = g_in__X__inh_spikes__tmp_;

    /**
     * spike updates due to convolutions
    **/

    S_.ode_state[State_::g_ex__X__exc_spikes] += ((0.001 * B_.spike_inputs_grid_sum_[EXC_SPIKES - MIN_SPIKE_RECEPTOR])) / (1 / 1000.0);
    S_.ode_state[State_::g_in__X__inh_spikes] += ((0.001 * B_.spike_inputs_grid_sum_[INH_SPIKES - MIN_SPIKE_RECEPTOR])) / (1 / 1000.0);

    /**
     * Begin NESTML generated code for the onCondition block(s)
    **/

    if ((!S_.is_refractory) && S_.ode_state[State_::V_m] >= P_.V_th)
    {
      S_.refr_t = P_.refr_T;
      S_.is_refractory = true;
      S_.ode_state[State_::V_m] = P_.V_reset;

      // begin generated code for emit_spike() function

      #ifdef DEBUG
      std::cout << "Emitting a spike at t = " << nest::Time(nest::Time::step(origin.get_steps() + lag + 1)).get_ms() << "\n";
      #endif
      set_spiketime(nest::Time::step(origin.get_steps() + lag + 1));
      nest::SpikeEvent se;
      nest::kernel().event_delivery_manager.send(*this, se, lag);
      // end generated code for emit_spike() function
    }
    if (S_.k_step <= P_.n_step && get_t() > P_.t_step[S_.k_step])
    {
      S_.I_step_now = P_.I_step[S_.k_step];
      S_.k_step += 1;
    }
    if (S_.is_refractory && S_.refr_t <= nest::Time::get_resolution().get_ms() / 2)
    {
      S_.refr_t = 0;
      S_.is_refractory = false;
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
void iaf_cond_exp_Istep_neuron::handle(nest::DataLoggingRequest& e)
{
  B_.logger_.handle(e);
}


void iaf_cond_exp_Istep_neuron::handle(nest::SpikeEvent &e)
{
#ifdef DEBUG
  std::cout << "[neuron " << this << "] iaf_cond_exp_Istep_neuron::handle(SpikeEvent)" << std::endl;
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
    if ( nestml_buffer_idx == iaf_cond_exp_Istep_neuron::PORT_NOT_AVAILABLE )
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

void iaf_cond_exp_Istep_neuron::handle(nest::CurrentEvent& e)
{
#ifdef DEBUG
  std::cout << "[neuron " << this << "] iaf_cond_exp_Istep_neuron::handle(CurrentEvent)" << std::endl;
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


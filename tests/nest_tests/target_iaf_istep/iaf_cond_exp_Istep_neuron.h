
/**
 *  iaf_cond_exp_Istep_neuron.h
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
#ifndef IAF_COND_EXP_ISTEP_NEURON
#define IAF_COND_EXP_ISTEP_NEURON

#ifndef HAVE_LIBLTDL
#error "NEST was compiled without support for dynamic loading. Please install libltdl and recompile NEST."
#endif

// C++ includes:
#include <cmath>

#include "config.h"

#ifndef HAVE_GSL
#error "The GSL library is required for the Runge-Kutta solver."
#endif

// External includes:
#include <gsl/gsl_errno.h>
#include <gsl/gsl_matrix.h>
#include <gsl/gsl_odeiv.h>

// Includes from nestkernel:
#include "archiving_node.h"
#include "connection.h"
#include "dict_util.h"
#include "event.h"
#include "nest_types.h"
#include "ring_buffer.h"
#include "universal_data_logger.h"

// Includes from sli:
#include "dictdatum.h"

// uncomment the next line to enable printing of detailed debug information
// #define DEBUG

namespace nest
{
namespace iaf_cond_exp_Istep_neuron_names
{
    const Name _V_m( "V_m" );
    const Name _refr_t( "refr_t" );
    const Name _is_refractory( "is_refractory" );
    const Name _k_step( "k_step" );
    const Name _I_step_now( "I_step_now" );
    const Name _g_ex__X__exc_spikes( "g_ex__X__exc_spikes" );
    const Name _g_in__X__inh_spikes( "g_in__X__inh_spikes" );
    const Name _V_th( "V_th" );
    const Name _V_reset( "V_reset" );
    const Name _refr_T( "refr_T" );
    const Name _g_L( "g_L" );
    const Name _C_m( "C_m" );
    const Name _E_ex( "E_ex" );
    const Name _E_in( "E_in" );
    const Name _E_L( "E_L" );
    const Name _tau_syn_ex( "tau_syn_ex" );
    const Name _tau_syn_in( "tau_syn_in" );
    const Name _I_e( "I_e" );
    const Name _n_step( "n_step" );
    const Name _I_step( "I_step" );
    const Name _t_step( "t_step" );

    const Name gsl_abs_error_tol("gsl_abs_error_tol");
    const Name gsl_rel_error_tol("gsl_rel_error_tol");
}
}



/**
 * Function computing right-hand side of ODE for GSL solver.
 * @note Must be declared here so we can befriend it in class.
 * @note Must have C-linkage for passing to GSL. Internally, it is
 *       a first-class C++ function, but cannot be a member function
 *       because of the C-linkage.
 * @note No point in declaring it inline, since it is called
 *       through a function pointer.
 * @param void* Pointer to model neuron instance.
 *
 * Integrate the variables: 
**/
extern "C" inline int iaf_cond_exp_Istep_neuron_dynamics( double, const double ode_state[], double f[], void* pnode );

#include "nest_time.h"
  typedef size_t nest_port_t;
  typedef size_t nest_rport_t;

/* BeginDocumentation
  Name: iaf_cond_exp_Istep_neuron

  Description:

    iaf_cond_exp_Istep_neuron - Simple conductance based leaky integrate-and-fire neuron model with step current
  ############################################################################################################

  Description
  +++++++++++

  This is a variation of iaf_cond_exp [1] that incorporates a stepwise-constant injected current, defined according to a vector of times (``t_step``) and a vector of current amplitudes at those times (``I_step``).

  References
  ++++++++++

  .. [1] Meffin H, Burkitt AN, Grayden DB (2004). An analytical
  model for the large, fluctuating synaptic conductance state typical of
  neocortical neurons in vivo. Journal of Computational Neuroscience,
  16:159-175.
  DOI: https://doi.org/10.1023/B:JCNS.0000014108.03012.81

  See also
  ++++++++

  iaf_psc_delta, iaf_psc_exp, iaf_cond_exp



  Parameters:
  The following parameters can be set in the status dictionary.
V_th [mV]  Threshold potential
V_reset [mV]  Reset potential
refr_T [ms]  Duration of refractory period
g_L [nS]  Leak conductance
C_m [pF]  Membrane capacitance
E_ex [mV]  Excitatory reversal potential
E_in [mV]  Inhibitory reversal potential
E_L [mV]  Leak reversal potential (aka resting potential)
tau_syn_ex [ms]  Synaptic time constant of excitatory synapse
tau_syn_in [ms]  Synaptic time constant of inhibitory synapse
I_e [pA] constant external input current
n_step [integer]  length of step current
I_step [pA]  injected current
t_step [ms]  times of step current changes


  Dynamic state variables:
V_m [mV]  membrane potential
refr_t [ms]  Refractory period timer
k_step [integer]  iterator for step current
I_step_now [pA]  momentaneous value of step current


  Sends: nest::SpikeEvent

  Receives: Spike, Current, DataLoggingRequest
*/

// Register the neuron model
void register_iaf_cond_exp_Istep_neuron( const std::string& name );

class iaf_cond_exp_Istep_neuron : public nest::ArchivingNode
{
public:
  /**
   * The constructor is only used to create the model prototype in the model manager.
  **/
  iaf_cond_exp_Istep_neuron();

  /**
   * The copy constructor is used to create model copies and instances of the model.
   * @node The copy constructor needs to initialize the parameters and the state.
   *       Initialization of buffers and interal variables is deferred to
   *       @c init_buffers_() and @c pre_run_hook() (or calibrate() in NEST 3.3 and older).
  **/
  iaf_cond_exp_Istep_neuron(const iaf_cond_exp_Istep_neuron &);

  /**
   * Destructor.
  **/
  ~iaf_cond_exp_Istep_neuron() override;

  // -------------------------------------------------------------------------
  //   Import sets of overloaded virtual functions.
  //   See: Technical Issues / Virtual Functions: Overriding, Overloading,
  //        and Hiding
  // -------------------------------------------------------------------------

  using nest::Node::handles_test_event;
  using nest::Node::handle;

  /**
   * Used to validate that we can send nest::SpikeEvent to desired target:port.
  **/
  nest_port_t send_test_event(nest::Node& target, nest_rport_t receptor_type, nest::synindex, bool) override;


  // -------------------------------------------------------------------------
  //   Functions handling incoming events.
  //   We tell nest that we can handle incoming events of various types by
  //   defining handle() for the given event.
  // -------------------------------------------------------------------------


  void handle(nest::SpikeEvent &) override;        //! accept spikes
  void handle(nest::CurrentEvent &) override;      //! accept input current

  void handle(nest::DataLoggingRequest &) override;//! allow recording with multimeter
  nest_port_t handles_test_event(nest::SpikeEvent&, nest_port_t) override;
  nest_port_t handles_test_event(nest::CurrentEvent&, nest_port_t) override;
  nest_port_t handles_test_event(nest::DataLoggingRequest&, nest_port_t) override;

  // -------------------------------------------------------------------------
  //   Functions for getting/setting parameters and state values.
  // -------------------------------------------------------------------------

  void get_status(DictionaryDatum &) const override;
  void set_status(const DictionaryDatum &) override;


  // -------------------------------------------------------------------------
  //   Getters/setters for state block
  // -------------------------------------------------------------------------

  inline double get_V_m() const
  {
    return S_.ode_state[State_::V_m];
  }

  inline void set_V_m(const double __v)
  {
    S_.ode_state[State_::V_m] = __v;
  }

  inline double get_refr_t() const
  {
    return S_.refr_t;
  }

  inline void set_refr_t(const double __v)
  {
    S_.refr_t = __v;
  }

  inline bool get_is_refractory() const
  {
    return S_.is_refractory;
  }

  inline void set_is_refractory(const bool __v)
  {
    S_.is_refractory = __v;
  }

  inline long get_k_step() const
  {
    return S_.k_step;
  }

  inline void set_k_step(const long __v)
  {
    S_.k_step = __v;
  }

  inline double get_I_step_now() const
  {
    return S_.I_step_now;
  }

  inline void set_I_step_now(const double __v)
  {
    S_.I_step_now = __v;
  }

  inline double get_g_ex__X__exc_spikes() const
  {
    return S_.ode_state[State_::g_ex__X__exc_spikes];
  }

  inline void set_g_ex__X__exc_spikes(const double __v)
  {
    S_.ode_state[State_::g_ex__X__exc_spikes] = __v;
  }

  inline double get_g_in__X__inh_spikes() const
  {
    return S_.ode_state[State_::g_in__X__inh_spikes];
  }

  inline void set_g_in__X__inh_spikes(const double __v)
  {
    S_.ode_state[State_::g_in__X__inh_spikes] = __v;
  }


  // -------------------------------------------------------------------------
  //   Getters/setters for parameters
  // -------------------------------------------------------------------------

  inline double get_V_th() const
  {
    return P_.V_th;
  }

  inline void set_V_th(const double __v)
  {
    P_.V_th = __v;
  }

  inline double get_V_reset() const
  {
    return P_.V_reset;
  }

  inline void set_V_reset(const double __v)
  {
    P_.V_reset = __v;
  }

  inline double get_refr_T() const
  {
    return P_.refr_T;
  }

  inline void set_refr_T(const double __v)
  {
    P_.refr_T = __v;
  }

  inline double get_g_L() const
  {
    return P_.g_L;
  }

  inline void set_g_L(const double __v)
  {
    P_.g_L = __v;
  }

  inline double get_C_m() const
  {
    return P_.C_m;
  }

  inline void set_C_m(const double __v)
  {
    P_.C_m = __v;
  }

  inline double get_E_ex() const
  {
    return P_.E_ex;
  }

  inline void set_E_ex(const double __v)
  {
    P_.E_ex = __v;
  }

  inline double get_E_in() const
  {
    return P_.E_in;
  }

  inline void set_E_in(const double __v)
  {
    P_.E_in = __v;
  }

  inline double get_E_L() const
  {
    return P_.E_L;
  }

  inline void set_E_L(const double __v)
  {
    P_.E_L = __v;
  }

  inline double get_tau_syn_ex() const
  {
    return P_.tau_syn_ex;
  }

  inline void set_tau_syn_ex(const double __v)
  {
    P_.tau_syn_ex = __v;
  }

  inline double get_tau_syn_in() const
  {
    return P_.tau_syn_in;
  }

  inline void set_tau_syn_in(const double __v)
  {
    P_.tau_syn_in = __v;
  }

  inline double get_I_e() const
  {
    return P_.I_e;
  }

  inline void set_I_e(const double __v)
  {
    P_.I_e = __v;
  }

  inline long get_n_step() const
  {
    return P_.n_step;
  }

  inline void set_n_step(const long __v)
  {
    P_.n_step = __v;
  }

  inline std::vector< double >  get_I_step() const
  {
    return P_.I_step;
  }

  inline void set_I_step(const std::vector< double >  __v)
  {
    P_.I_step = __v;
  }

  inline std::vector< double >  get_t_step() const
  {
    return P_.t_step;
  }

  inline void set_t_step(const std::vector< double >  __v)
  {
    P_.t_step = __v;
  }


  // -------------------------------------------------------------------------
  //   Getters/setters for internals
  // -------------------------------------------------------------------------

  inline double get___h() const
  {
    return V_.__h;
  }

  inline void set___h(const double __v)
  {
    V_.__h = __v;
  }
  inline double get___P__g_ex__X__exc_spikes__g_ex__X__exc_spikes() const
  {
    return V_.__P__g_ex__X__exc_spikes__g_ex__X__exc_spikes;
  }

  inline void set___P__g_ex__X__exc_spikes__g_ex__X__exc_spikes(const double __v)
  {
    V_.__P__g_ex__X__exc_spikes__g_ex__X__exc_spikes = __v;
  }
  inline double get___P__g_in__X__inh_spikes__g_in__X__inh_spikes() const
  {
    return V_.__P__g_in__X__inh_spikes__g_in__X__inh_spikes;
  }

  inline void set___P__g_in__X__inh_spikes__g_in__X__inh_spikes(const double __v)
  {
    V_.__P__g_in__X__inh_spikes__g_in__X__inh_spikes = __v;
  }


  // -------------------------------------------------------------------------
  //   Methods corresponding to event handlers
  // -------------------------------------------------------------------------

  

  // -------------------------------------------------------------------------
  //   Initialization functions
  // -------------------------------------------------------------------------
  void calibrate_time( const nest::TimeConverter& tc ) override;

protected:

private:
  void recompute_internal_variables(bool exclude_timestep=false);

private:

  static const nest_port_t MIN_SPIKE_RECEPTOR = 0;
  static const nest_port_t PORT_NOT_AVAILABLE = -1;

  enum SynapseTypes
  {
    INH_SPIKES = 0,
    EXC_SPIKES = 1,
    MAX_SPIKE_RECEPTOR = 2
  };

  static const size_t NUM_SPIKE_RECEPTORS = MAX_SPIKE_RECEPTOR - MIN_SPIKE_RECEPTOR;

static std::vector< std::tuple< int, int > > rport_to_nestml_buffer_idx;

  /**
   * Reset state of neuron.
  **/

  void init_state_internal_();

  /**
   * Reset internal buffers of neuron.
  **/
  void init_buffers_() override;

  /**
   * Initialize auxiliary quantities, leave parameters and state untouched.
  **/
  void pre_run_hook() override;

  /**
   * Take neuron through given time interval
  **/
  void update(nest::Time const &, const long, const long) override;

  // The next two classes need to be friends to access the State_ class/member
  friend class nest::RecordablesMap<iaf_cond_exp_Istep_neuron>;
  friend class nest::UniversalDataLogger<iaf_cond_exp_Istep_neuron>;

  /**
   * Free parameters of the neuron.
   *


   *
   * These are the parameters that can be set by the user through @c `node.set()`.
   * They are initialized from the model prototype when the node is created.
   * Parameters do not change during calls to @c update() and are not reset by
   * @c ResetNetwork.
   *
   * @note Parameters_ need neither copy constructor nor @c operator=(), since
   *       all its members are copied properly by the default copy constructor
   *       and assignment operator. Important:
   *       - If Parameters_ contained @c Time members, you need to define the
   *         assignment operator to recalibrate all members of type @c Time . You
   *         may also want to define the assignment operator.
   *       - If Parameters_ contained members that cannot copy themselves, such
   *         as C-style arrays, you need to define the copy constructor and
   *         assignment operator to copy those members.
  **/
  struct Parameters_
  {    
    //!  Threshold potential
    double V_th;
    //!  Reset potential
    double V_reset;
    //!  Duration of refractory period
    double refr_T;
    //!  Leak conductance
    double g_L;
    //!  Membrane capacitance
    double C_m;
    //!  Excitatory reversal potential
    double E_ex;
    //!  Inhibitory reversal potential
    double E_in;
    //!  Leak reversal potential (aka resting potential)
    double E_L;
    //!  Synaptic time constant of excitatory synapse
    double tau_syn_ex;
    //!  Synaptic time constant of inhibitory synapse
    double tau_syn_in;
    //! constant external input current
    double I_e;
    //!  length of step current
    long n_step;
    //!  injected current
    std::vector< double >  I_step;
    //!  times of step current changes
    std::vector< double >  t_step;

    double __gsl_abs_error_tol;
    double __gsl_rel_error_tol;

    /**
     * Initialize parameters to their default values.
    **/
    Parameters_();
  };

  /**
   * Dynamic state of the neuron.
   *
   *
   *
   * These are the state variables that are advanced in time by calls to
   * @c update(). In many models, some or all of them can be set by the user
   * through @c `node.set()`. The state variables are initialized from the model
   * prototype when the node is created. State variables are reset by @c ResetNetwork.
   *
   * @note State_ need neither copy constructor nor @c operator=(), since
   *       all its members are copied properly by the default copy constructor
   *       and assignment operator. Important:
   *       - If State_ contained @c Time members, you need to define the
   *         assignment operator to recalibrate all members of type @c Time . You
   *         may also want to define the assignment operator.
   *       - If State_ contained members that cannot copy themselves, such
   *         as C-style arrays, you need to define the copy constructor and
   *         assignment operator to copy those members.
  **/
  struct State_
  {

    // non-ODE state variables
//!  Refractory period timer
double refr_t;
bool is_refractory;
//!  iterator for step current
long k_step;
//!  momentaneous value of step current
double I_step_now;
    //! Symbolic indices to the elements of the state vector y
    enum StateVecElems
    {
      V_m,
      g_ex__X__exc_spikes,
      g_in__X__inh_spikes,
      // moved state variables from synapse (numeric)
      // moved state variables from synapse (analytic)
      // final entry to easily get the vector size
      STATE_VEC_SIZE
    };

    //! state vector, must be C-array for GSL solver
    double ode_state[STATE_VEC_SIZE];

    State_();
  };

  struct DelayedVariables_
  {
  };

  /**
   * Internal variables of the neuron.
   *
   *
   *
   * These variables must be initialized by @c pre_run_hook (or calibrate in NEST 3.3 and older), which is called before
   * the first call to @c update() upon each call to @c Simulate.
   * @node Variables_ needs neither constructor, copy constructor or assignment operator,
   *       since it is initialized by @c pre_run_hook() (or calibrate() in NEST 3.3 and older). If Variables_ has members that
   *       cannot destroy themselves, Variables_ will need a destructor.
  **/
  struct Variables_
  {
    double __h;
    double __P__g_ex__X__exc_spikes__g_ex__X__exc_spikes;
    double __P__g_in__X__inh_spikes__g_in__X__inh_spikes;
  };

  /**
   * Buffers of the neuron.
   * Usually buffers for incoming spikes and data logged for analog recorders.
   * Buffers must be initialized by @c init_buffers_(), which is called before
   * @c pre_run_hook() (or calibrate() in NEST 3.3 and older) on the first call to @c Simulate after the start of NEST,
   * ResetKernel or ResetNetwork.
   * @node Buffers_ needs neither constructor, copy constructor or assignment operator,
   *       since it is initialized by @c init_nodes_(). If Buffers_ has members that
   *       cannot destroy themselves, Buffers_ will need a destructor.
  **/
  struct Buffers_
  {
    Buffers_(iaf_cond_exp_Istep_neuron &);
    Buffers_(const Buffers_ &, iaf_cond_exp_Istep_neuron &);

    /**
     * Logger for all analog data
    **/
    nest::UniversalDataLogger<iaf_cond_exp_Istep_neuron> logger_;

    // -----------------------------------------------------------------------
    //   Spike buffers and sums of incoming spikes/currents per timestep
    // -----------------------------------------------------------------------    



    /**
     * Buffer containing the incoming spikes
    **/
    inline std::vector< nest::RingBuffer >& get_spike_inputs_()
    {
        return spike_inputs_;
    }
    std::vector< nest::RingBuffer > spike_inputs_;

    /**
     * Buffer containing the sum of all the incoming spikes
    **/
    inline std::vector< double >& get_spike_inputs_grid_sum_()
    {
        return spike_inputs_grid_sum_;
    }
    std::vector< double > spike_inputs_grid_sum_;

    /**
     * Buffer containing a flag whether incoming spikes have been received on a given port
    **/
    inline std::vector< nest::RingBuffer >& get_spike_input_received_()
    {
        return spike_input_received_;
    }
    std::vector< nest::RingBuffer > spike_input_received_;

    /**
     * Buffer containing a flag whether incoming spikes have been received on a given port
    **/
    inline std::vector< double >& get_spike_input_received_grid_sum_()
    {
        return spike_input_received_grid_sum_;
    }
    std::vector< double > spike_input_received_grid_sum_;

    // -----------------------------------------------------------------------
    //   Continuous-input buffers
    // -----------------------------------------------------------------------

    

    nest::RingBuffer
     I_stim;   //!< Buffer for input (type: pA)

    inline nest::RingBuffer& get_I_stim() {
        return I_stim;
    }

    double I_stim_grid_sum_;

    // -----------------------------------------------------------------------
    //   GSL ODE solver data structures
    // -----------------------------------------------------------------------

    gsl_odeiv_step* __s;    //!< stepping function
    gsl_odeiv_control* __c; //!< adaptive stepsize control function
    gsl_odeiv_evolve* __e;  //!< evolution function
    gsl_odeiv_system __sys; //!< struct describing system

    // __integration_step should be reset with the neuron on ResetNetwork,
    // but remain unchanged during calibration. Since it is initialized with
    // step_, and the resolution cannot change after nodes have been created,
    // it is safe to place both here.
    double __step;             //!< step size in ms
    double __integration_step; //!< current integration time step, updated by GSL
  };

  // -------------------------------------------------------------------------
  //   Getters/setters for inline expressions
  // -------------------------------------------------------------------------

  inline double get_I_syn_ex() const
  {
    return S_.ode_state[State_::g_ex__X__exc_spikes] * 1.0 * (S_.ode_state[State_::V_m] - P_.E_ex);
  }

  inline double get_I_syn_in() const
  {
    return S_.ode_state[State_::g_in__X__inh_spikes] * 1.0 * (S_.ode_state[State_::V_m] - P_.E_in);
  }

  inline double get_I_leak() const
  {
    return P_.g_L * (S_.ode_state[State_::V_m] - P_.E_L);
  }



  // -------------------------------------------------------------------------
  //   Getters/setters for input buffers
  // -------------------------------------------------------------------------  




  /**
   * Buffer containing the incoming spikes
  **/
  inline std::vector< nest::RingBuffer >& get_spike_inputs_()
  {
      return B_.get_spike_inputs_();
  }

  /**
   * Buffer containing the sum of all the incoming spikes
  **/
  inline std::vector< double >& get_spike_inputs_grid_sum_()
  {
      return B_.get_spike_inputs_grid_sum_();
  }

  /**
   * Buffer containing a flag whether incoming spikes have been received on a given port
  **/
  inline std::vector< nest::RingBuffer >& get_spike_input_received_()
  {
      return B_.get_spike_input_received_();
  }

  /**
   * Buffer containing a flag whether incoming spikes have been received on a given port
  **/
  inline std::vector< double >& get_spike_input_received_grid_sum_()
  {
      return B_.get_spike_input_received_grid_sum_();
  }

inline nest::RingBuffer& get_I_stim() {
    return B_.get_I_stim();
}

  // -------------------------------------------------------------------------
  //   Member variables of neuron model.
  //   Each model neuron should have precisely the following four data members,
  //   which are one instance each of the parameters, state, buffers and variables
  //   structures. Experience indicates that the state and variables member should
  //   be next to each other to achieve good efficiency (caching).
  //   Note: Devices require one additional data member, an instance of the
  //   ``Device`` child class they belong to.
  // -------------------------------------------------------------------------


  Parameters_       P_;        //!< Free parameters.
  State_            S_;        //!< Dynamic state.
  DelayedVariables_ DV_;       //!< Delayed state variables.
  Variables_        V_;        //!< Internal Variables
  Buffers_          B_;        //!< Buffers.

  //! Mapping of recordables names to access functions
  static nest::RecordablesMap<iaf_cond_exp_Istep_neuron> recordablesMap_;
  friend int iaf_cond_exp_Istep_neuron_dynamics( double, const double ode_state[], double f[], void* pnode );

}; /* neuron iaf_cond_exp_Istep_neuron */

inline nest_port_t iaf_cond_exp_Istep_neuron::send_test_event(nest::Node& target, nest_rport_t receptor_type, nest::synindex, bool)
{
  // You should usually not change the code in this function.
  // It confirms that the target of connection @c c accepts @c nest::SpikeEvent on
  // the given @c receptor_type.
  nest::SpikeEvent e;
  e.set_sender(*this);
  return target.handles_test_event(e, receptor_type);
}

inline nest_port_t iaf_cond_exp_Istep_neuron::handles_test_event(nest::SpikeEvent&, nest_port_t receptor_type)
{
    // You should usually not change the code in this function.
    // It confirms to the connection management system that we are able
    // to handle @c SpikeEvent on port 0. You need to extend the function
    // if you want to differentiate between input ports.
    if (receptor_type != 0)
    {
      throw nest::UnknownReceptorType(receptor_type, get_name());
    }
    return 0;
}

inline nest_port_t iaf_cond_exp_Istep_neuron::handles_test_event(nest::CurrentEvent&, nest_port_t receptor_type)
{
  // You should usually not change the code in this function.
  // It confirms to the connection management system that we are able
  // to handle @c CurrentEvent on port 0. You need to extend the function
  // if you want to differentiate between input ports.
  if (receptor_type != 0)
  {
    throw nest::UnknownReceptorType(receptor_type, get_name());
  }
  return 0;
}

inline nest_port_t iaf_cond_exp_Istep_neuron::handles_test_event(nest::DataLoggingRequest& dlr, nest_port_t receptor_type)
{
  // You should usually not change the code in this function.
  // It confirms to the connection management system that we are able
  // to handle @c DataLoggingRequest on port 0.
  // The function also tells the built-in UniversalDataLogger that this node
  // is recorded from and that it thus needs to collect data during simulation.
  if (receptor_type != 0)
  {
    throw nest::UnknownReceptorType(receptor_type, get_name());
  }

  return B_.logger_.connect_logging_device(dlr, recordablesMap_);
}

inline void iaf_cond_exp_Istep_neuron::get_status(DictionaryDatum &__d) const
{
  // parameters
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_V_th, get_V_th());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_V_reset, get_V_reset());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_refr_T, get_refr_T());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_g_L, get_g_L());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_C_m, get_C_m());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_E_ex, get_E_ex());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_E_in, get_E_in());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_E_L, get_E_L());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_tau_syn_ex, get_tau_syn_ex());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_tau_syn_in, get_tau_syn_in());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_I_e, get_I_e());
  def< long >(__d, nest::iaf_cond_exp_Istep_neuron_names::_n_step, get_n_step());
  def< std::vector< double >  >(__d, nest::iaf_cond_exp_Istep_neuron_names::_I_step, get_I_step());
  def< std::vector< double >  >(__d, nest::iaf_cond_exp_Istep_neuron_names::_t_step, get_t_step());

  // initial values for state variables in ODE or kernel
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_V_m, get_V_m());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_refr_t, get_refr_t());
  def< bool >(__d, nest::iaf_cond_exp_Istep_neuron_names::_is_refractory, get_is_refractory());
  def< long >(__d, nest::iaf_cond_exp_Istep_neuron_names::_k_step, get_k_step());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_I_step_now, get_I_step_now());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_g_ex__X__exc_spikes, get_g_ex__X__exc_spikes());
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::_g_in__X__inh_spikes, get_g_in__X__inh_spikes());

  ArchivingNode::get_status( __d );

  (*__d)[nest::names::recordables] = recordablesMap_.get_list();
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::gsl_abs_error_tol, P_.__gsl_abs_error_tol);
  if ( P_.__gsl_abs_error_tol <= 0. ){
    throw nest::BadProperty( "The gsl_abs_error_tol must be strictly positive." );
  }
  def< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::gsl_rel_error_tol, P_.__gsl_rel_error_tol);
  if ( P_.__gsl_rel_error_tol < 0. ){
    throw nest::BadProperty( "The gsl_rel_error_tol must be zero or positive." );
  }
}

inline void iaf_cond_exp_Istep_neuron::set_status(const DictionaryDatum &__d)
{
  // parameters
  double tmp_V_th = get_V_th();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_V_th, tmp_V_th, this);
  // Resize vectors
  if (tmp_V_th != get_V_th())
  {
  }
  double tmp_V_reset = get_V_reset();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_V_reset, tmp_V_reset, this);
  // Resize vectors
  if (tmp_V_reset != get_V_reset())
  {
  }
  double tmp_refr_T = get_refr_T();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_refr_T, tmp_refr_T, this);
  // Resize vectors
  if (tmp_refr_T != get_refr_T())
  {
  }
  double tmp_g_L = get_g_L();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_g_L, tmp_g_L, this);
  // Resize vectors
  if (tmp_g_L != get_g_L())
  {
  }
  double tmp_C_m = get_C_m();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_C_m, tmp_C_m, this);
  // Resize vectors
  if (tmp_C_m != get_C_m())
  {
  }
  double tmp_E_ex = get_E_ex();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_E_ex, tmp_E_ex, this);
  // Resize vectors
  if (tmp_E_ex != get_E_ex())
  {
  }
  double tmp_E_in = get_E_in();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_E_in, tmp_E_in, this);
  // Resize vectors
  if (tmp_E_in != get_E_in())
  {
  }
  double tmp_E_L = get_E_L();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_E_L, tmp_E_L, this);
  // Resize vectors
  if (tmp_E_L != get_E_L())
  {
  }
  double tmp_tau_syn_ex = get_tau_syn_ex();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_tau_syn_ex, tmp_tau_syn_ex, this);
  // Resize vectors
  if (tmp_tau_syn_ex != get_tau_syn_ex())
  {
  }
  double tmp_tau_syn_in = get_tau_syn_in();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_tau_syn_in, tmp_tau_syn_in, this);
  // Resize vectors
  if (tmp_tau_syn_in != get_tau_syn_in())
  {
  }
  double tmp_I_e = get_I_e();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_I_e, tmp_I_e, this);
  // Resize vectors
  if (tmp_I_e != get_I_e())
  {
  }
  long tmp_n_step = get_n_step();
  nest::updateValueParam<long>(__d, nest::iaf_cond_exp_Istep_neuron_names::_n_step, tmp_n_step, this);
  // Resize vectors
  if (tmp_n_step != get_n_step())
  {
    std::vector< double >  _tmp_I_step = get_I_step();
    _tmp_I_step.resize(tmp_n_step, 0.);
    set_I_step(_tmp_I_step);
    std::vector< double >  _tmp_t_step = get_t_step();
    _tmp_t_step.resize(tmp_n_step, 0.);
    set_t_step(_tmp_t_step);
  }
  std::vector< double >  tmp_I_step = get_I_step();
  updateValue<std::vector< double > >(__d, nest::iaf_cond_exp_Istep_neuron_names::_I_step, tmp_I_step);
  // Resize vectors
  if (tmp_I_step != get_I_step())
  {
  }
   
  // Check if the new vector size matches its original size
  if ( tmp_I_step.size() != tmp_n_step )
  {
    std::stringstream msg;
    msg << "The vector \"I_step\" does not match its size: " << tmp_n_step;
    throw nest::BadProperty(msg.str());
  }
  std::vector< double >  tmp_t_step = get_t_step();
  updateValue<std::vector< double > >(__d, nest::iaf_cond_exp_Istep_neuron_names::_t_step, tmp_t_step);
  // Resize vectors
  if (tmp_t_step != get_t_step())
  {
  }
   
  // Check if the new vector size matches its original size
  if ( tmp_t_step.size() != tmp_n_step )
  {
    std::stringstream msg;
    msg << "The vector \"t_step\" does not match its size: " << tmp_n_step;
    throw nest::BadProperty(msg.str());
  }

  // initial values for state variables in ODE or kernel
  double tmp_V_m = get_V_m();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_V_m, tmp_V_m, this);
  double tmp_refr_t = get_refr_t();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_refr_t, tmp_refr_t, this);
  bool tmp_is_refractory = get_is_refractory();
  nest::updateValueParam<bool>(__d, nest::iaf_cond_exp_Istep_neuron_names::_is_refractory, tmp_is_refractory, this);
  long tmp_k_step = get_k_step();
  nest::updateValueParam<long>(__d, nest::iaf_cond_exp_Istep_neuron_names::_k_step, tmp_k_step, this);
  double tmp_I_step_now = get_I_step_now();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_I_step_now, tmp_I_step_now, this);
  double tmp_g_ex__X__exc_spikes = get_g_ex__X__exc_spikes();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_g_ex__X__exc_spikes, tmp_g_ex__X__exc_spikes, this);
  double tmp_g_in__X__inh_spikes = get_g_in__X__inh_spikes();
  nest::updateValueParam<double>(__d, nest::iaf_cond_exp_Istep_neuron_names::_g_in__X__inh_spikes, tmp_g_in__X__inh_spikes, this);

  // We now know that (ptmp, stmp) are consistent. We do not
  // write them back to (P_, S_) before we are also sure that
  // the properties to be set in the parent class are internally
  // consistent.
  ArchivingNode::set_status(__d);

  // if we get here, temporaries contain consistent set of properties
  set_V_th(tmp_V_th);
  set_V_reset(tmp_V_reset);
  set_refr_T(tmp_refr_T);
  set_g_L(tmp_g_L);
  set_C_m(tmp_C_m);
  set_E_ex(tmp_E_ex);
  set_E_in(tmp_E_in);
  set_E_L(tmp_E_L);
  set_tau_syn_ex(tmp_tau_syn_ex);
  set_tau_syn_in(tmp_tau_syn_in);
  set_I_e(tmp_I_e);
  set_n_step(tmp_n_step);
  set_I_step(tmp_I_step);
  set_t_step(tmp_t_step);
  set_V_m(tmp_V_m);
  set_refr_t(tmp_refr_t);
  set_is_refractory(tmp_is_refractory);
  set_k_step(tmp_k_step);
  set_I_step_now(tmp_I_step_now);
  set_g_ex__X__exc_spikes(tmp_g_ex__X__exc_spikes);
  set_g_in__X__inh_spikes(tmp_g_in__X__inh_spikes);




  updateValue< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::gsl_abs_error_tol, P_.__gsl_abs_error_tol);
  if ( P_.__gsl_abs_error_tol <= 0. )
  {
    throw nest::BadProperty( "The gsl_abs_error_tol must be strictly positive." );
  }
  updateValue< double >(__d, nest::iaf_cond_exp_Istep_neuron_names::gsl_rel_error_tol, P_.__gsl_rel_error_tol);
  if ( P_.__gsl_rel_error_tol < 0. )
  {
    throw nest::BadProperty( "The gsl_rel_error_tol must be zero or positive." );
  }

  // recompute internal variables in case they are dependent on parameters or state that might have been updated in this call to set_status()
  recompute_internal_variables();
};



#endif /* #ifndef IAF_COND_EXP_ISTEP_NEURON */

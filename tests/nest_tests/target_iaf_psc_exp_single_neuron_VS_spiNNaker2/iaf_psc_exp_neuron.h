
/**
 *  iaf_psc_exp_neuron.h
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
#ifndef IAF_PSC_EXP_NEURON
#define IAF_PSC_EXP_NEURON

#ifndef HAVE_LIBLTDL
#error "NEST was compiled without support for dynamic loading. Please install libltdl and recompile NEST."
#endif

// C++ includes:
#include <cmath>

#include "config.h"

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
namespace iaf_psc_exp_neuron_names
{
    const Name _V_m( "V_m" );
    const Name _refr_t( "refr_t" );
    const Name _I_syn_exc( "I_syn_exc" );
    const Name _I_syn_inh( "I_syn_inh" );
    const Name _C_m( "C_m" );
    const Name _tau_m( "tau_m" );
    const Name _tau_syn_inh( "tau_syn_inh" );
    const Name _tau_syn_exc( "tau_syn_exc" );
    const Name _refr_T( "refr_T" );
    const Name _E_L( "E_L" );
    const Name _V_reset( "V_reset" );
    const Name _V_th( "V_th" );
    const Name _I_e( "I_e" );

    const Name gsl_abs_error_tol("gsl_abs_error_tol");
    const Name gsl_rel_error_tol("gsl_rel_error_tol");
}
}




#include "nest_time.h"
  typedef size_t nest_port_t;
  typedef size_t nest_rport_t;

/* BeginDocumentation
  Name: iaf_psc_exp_neuron

  Description:

    iaf_psc_exp - Leaky integrate-and-fire neuron model
  ###################################################

  Description
  +++++++++++

  iaf_psc_exp is an implementation of a leaky integrate-and-fire model
  with exponentially decaying synaptic currents according to [1]_.
  Thus, postsynaptic currents have an infinitely short rise time.

  The threshold crossing is followed by an absolute refractory period
  during which the membrane potential is clamped to the resting potential
  and spiking is prohibited.

  The general framework for the consistent formulation of systems with
  neuron like dynamics interacting by point events is described in
  [1]_.  A flow chart can be found in [2]_.

  Critical tests for the formulation of the neuron model are the
  comparisons of simulation results for different computation step
  sizes.

  .. note::
  If tau_m is very close to tau_syn_exc or tau_syn_inh, numerical problems
  may arise due to singularities in the propagator matrics. If this is
  the case, replace equal-valued parameters by a single parameter.

  For details, please see ``IAF_neurons_singularity.ipynb`` in
  the NEST source code (``docs/model_details``).


  References
  ++++++++++

  .. [1] Rotter S,  Diesmann M (1999). Exact simulation of
  time-invariant linear systems with applications to neuronal
  modeling. Biologial Cybernetics 81:381-402.
  DOI: https://doi.org/10.1007/s004220050570
  .. [2] Diesmann M, Gewaltig M-O, Rotter S, & Aertsen A (2001). State
  space analysis of synchronous spiking in cortical neural
  networks. Neurocomputing 38-40:565-571.
  DOI: https://doi.org/10.1016/S0925-2312(01)00409-X
  .. [3] Morrison A, Straube S, Plesser H E, Diesmann M (2006). Exact
  subthreshold integration with continuous spike times in discrete time
  neural network simulations. Neural Computation, in press
  DOI: https://doi.org/10.1162/neco.2007.19.1.47


  See also
  ++++++++

  iaf_psc_delta, iaf_psc_alpha, iaf_cond_exp




  Parameters:
  The following parameters can be set in the status dictionary.
C_m [pF]  Capacitance of the membrane
tau_m [ms]  Membrane time constant
tau_syn_inh [ms]  Time constant of inhibitory synaptic current
tau_syn_exc [ms]  Time constant of excitatory synaptic current
refr_T [ms]  Duration of refractory period
E_L [mV]  Resting potential
V_reset [mV]  Reset value of the membrane potential
V_th [mV]  Spike threshold potential
I_e [pA] constant external input current


  Dynamic state variables:
V_m [mV]  Membrane potential
refr_t [ms]  Refractory period timer


  Sends: nest::SpikeEvent

  Receives: Spike, Current, DataLoggingRequest
*/

// Register the neuron model
void register_iaf_psc_exp_neuron( const std::string& name );

class iaf_psc_exp_neuron : public nest::ArchivingNode
{
public:
  /**
   * The constructor is only used to create the model prototype in the model manager.
  **/
  iaf_psc_exp_neuron();

  /**
   * The copy constructor is used to create model copies and instances of the model.
   * @node The copy constructor needs to initialize the parameters and the state.
   *       Initialization of buffers and interal variables is deferred to
   *       @c init_buffers_() and @c pre_run_hook() (or calibrate() in NEST 3.3 and older).
  **/
  iaf_psc_exp_neuron(const iaf_psc_exp_neuron &);

  /**
   * Destructor.
  **/
  ~iaf_psc_exp_neuron() override;

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
    return S_.V_m;
  }

  inline void set_V_m(const double __v)
  {
    S_.V_m = __v;
  }

  inline double get_refr_t() const
  {
    return S_.refr_t;
  }

  inline void set_refr_t(const double __v)
  {
    S_.refr_t = __v;
  }

  inline double get_I_syn_exc() const
  {
    return S_.I_syn_exc;
  }

  inline void set_I_syn_exc(const double __v)
  {
    S_.I_syn_exc = __v;
  }

  inline double get_I_syn_inh() const
  {
    return S_.I_syn_inh;
  }

  inline void set_I_syn_inh(const double __v)
  {
    S_.I_syn_inh = __v;
  }


  // -------------------------------------------------------------------------
  //   Getters/setters for parameters
  // -------------------------------------------------------------------------

  inline double get_C_m() const
  {
    return P_.C_m;
  }

  inline void set_C_m(const double __v)
  {
    P_.C_m = __v;
  }

  inline double get_tau_m() const
  {
    return P_.tau_m;
  }

  inline void set_tau_m(const double __v)
  {
    P_.tau_m = __v;
  }

  inline double get_tau_syn_inh() const
  {
    return P_.tau_syn_inh;
  }

  inline void set_tau_syn_inh(const double __v)
  {
    P_.tau_syn_inh = __v;
  }

  inline double get_tau_syn_exc() const
  {
    return P_.tau_syn_exc;
  }

  inline void set_tau_syn_exc(const double __v)
  {
    P_.tau_syn_exc = __v;
  }

  inline double get_refr_T() const
  {
    return P_.refr_T;
  }

  inline void set_refr_T(const double __v)
  {
    P_.refr_T = __v;
  }

  inline double get_E_L() const
  {
    return P_.E_L;
  }

  inline void set_E_L(const double __v)
  {
    P_.E_L = __v;
  }

  inline double get_V_reset() const
  {
    return P_.V_reset;
  }

  inline void set_V_reset(const double __v)
  {
    P_.V_reset = __v;
  }

  inline double get_V_th() const
  {
    return P_.V_th;
  }

  inline void set_V_th(const double __v)
  {
    P_.V_th = __v;
  }

  inline double get_I_e() const
  {
    return P_.I_e;
  }

  inline void set_I_e(const double __v)
  {
    P_.I_e = __v;
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
  inline double get___P__I_syn_exc__I_syn_exc() const
  {
    return V_.__P__I_syn_exc__I_syn_exc;
  }

  inline void set___P__I_syn_exc__I_syn_exc(const double __v)
  {
    V_.__P__I_syn_exc__I_syn_exc = __v;
  }
  inline double get___P__I_syn_inh__I_syn_inh() const
  {
    return V_.__P__I_syn_inh__I_syn_inh;
  }

  inline void set___P__I_syn_inh__I_syn_inh(const double __v)
  {
    V_.__P__I_syn_inh__I_syn_inh = __v;
  }
  inline double get___P__V_m__I_syn_exc() const
  {
    return V_.__P__V_m__I_syn_exc;
  }

  inline void set___P__V_m__I_syn_exc(const double __v)
  {
    V_.__P__V_m__I_syn_exc = __v;
  }
  inline double get___P__V_m__I_syn_inh() const
  {
    return V_.__P__V_m__I_syn_inh;
  }

  inline void set___P__V_m__I_syn_inh(const double __v)
  {
    V_.__P__V_m__I_syn_inh = __v;
  }
  inline double get___P__V_m__V_m() const
  {
    return V_.__P__V_m__V_m;
  }

  inline void set___P__V_m__V_m(const double __v)
  {
    V_.__P__V_m__V_m = __v;
  }
  inline double get___P__refr_t__refr_t() const
  {
    return V_.__P__refr_t__refr_t;
  }

  inline void set___P__refr_t__refr_t(const double __v)
  {
    V_.__P__refr_t__refr_t = __v;
  }


  // -------------------------------------------------------------------------
  //   Methods corresponding to event handlers
  // -------------------------------------------------------------------------

  
      void on_receive_block_exc_spikes();
      void on_receive_block_inh_spikes();

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
    EXC_SPIKES = 0,
    INH_SPIKES = 1,
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
  friend class nest::RecordablesMap<iaf_psc_exp_neuron>;
  friend class nest::UniversalDataLogger<iaf_psc_exp_neuron>;

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
    //!  Capacitance of the membrane
    double C_m;
    //!  Membrane time constant
    double tau_m;
    //!  Time constant of inhibitory synaptic current
    double tau_syn_inh;
    //!  Time constant of excitatory synaptic current
    double tau_syn_exc;
    //!  Duration of refractory period
    double refr_T;
    //!  Resting potential
    double E_L;
    //!  Reset value of the membrane potential
    double V_reset;
    //!  Spike threshold potential
    double V_th;
    //! constant external input current
    double I_e;

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
    //!  Membrane potential
    double V_m;
    //!  Refractory period timer
    double refr_t;
    double I_syn_exc;
    double I_syn_inh;

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
    double __P__I_syn_exc__I_syn_exc;
    double __P__I_syn_inh__I_syn_inh;
    double __P__V_m__I_syn_exc;
    double __P__V_m__I_syn_inh;
    double __P__V_m__V_m;
    double __P__refr_t__refr_t;
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
    Buffers_(iaf_psc_exp_neuron &);
    Buffers_(const Buffers_ &, iaf_psc_exp_neuron &);

    /**
     * Logger for all analog data
    **/
    nest::UniversalDataLogger<iaf_psc_exp_neuron> logger_;

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
  };

  // -------------------------------------------------------------------------
  //   Getters/setters for inline expressions
  // -------------------------------------------------------------------------

  

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
  static nest::RecordablesMap<iaf_psc_exp_neuron> recordablesMap_;

}; /* neuron iaf_psc_exp_neuron */

inline nest_port_t iaf_psc_exp_neuron::send_test_event(nest::Node& target, nest_rport_t receptor_type, nest::synindex, bool)
{
  // You should usually not change the code in this function.
  // It confirms that the target of connection @c c accepts @c nest::SpikeEvent on
  // the given @c receptor_type.
  nest::SpikeEvent e;
  e.set_sender(*this);
  return target.handles_test_event(e, receptor_type);
}

inline nest_port_t iaf_psc_exp_neuron::handles_test_event(nest::SpikeEvent&, nest_port_t receptor_type)
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

inline nest_port_t iaf_psc_exp_neuron::handles_test_event(nest::CurrentEvent&, nest_port_t receptor_type)
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

inline nest_port_t iaf_psc_exp_neuron::handles_test_event(nest::DataLoggingRequest& dlr, nest_port_t receptor_type)
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

inline void iaf_psc_exp_neuron::get_status(DictionaryDatum &__d) const
{
  // parameters
  def< double >(__d, nest::iaf_psc_exp_neuron_names::_C_m, get_C_m());
  def< double >(__d, nest::iaf_psc_exp_neuron_names::_tau_m, get_tau_m());
  def< double >(__d, nest::iaf_psc_exp_neuron_names::_tau_syn_inh, get_tau_syn_inh());
  def< double >(__d, nest::iaf_psc_exp_neuron_names::_tau_syn_exc, get_tau_syn_exc());
  def< double >(__d, nest::iaf_psc_exp_neuron_names::_refr_T, get_refr_T());
  def< double >(__d, nest::iaf_psc_exp_neuron_names::_E_L, get_E_L());
  def< double >(__d, nest::iaf_psc_exp_neuron_names::_V_reset, get_V_reset());
  def< double >(__d, nest::iaf_psc_exp_neuron_names::_V_th, get_V_th());
  def< double >(__d, nest::iaf_psc_exp_neuron_names::_I_e, get_I_e());

  // initial values for state variables in ODE or kernel
  def< double >(__d, nest::iaf_psc_exp_neuron_names::_V_m, get_V_m());
  def< double >(__d, nest::iaf_psc_exp_neuron_names::_refr_t, get_refr_t());
  def< double >(__d, nest::iaf_psc_exp_neuron_names::_I_syn_exc, get_I_syn_exc());
  def< double >(__d, nest::iaf_psc_exp_neuron_names::_I_syn_inh, get_I_syn_inh());

  ArchivingNode::get_status( __d );

  (*__d)[nest::names::recordables] = recordablesMap_.get_list();
}

inline void iaf_psc_exp_neuron::set_status(const DictionaryDatum &__d)
{
  // parameters
  double tmp_C_m = get_C_m();
  nest::updateValueParam<double>(__d, nest::iaf_psc_exp_neuron_names::_C_m, tmp_C_m, this);
  double tmp_tau_m = get_tau_m();
  nest::updateValueParam<double>(__d, nest::iaf_psc_exp_neuron_names::_tau_m, tmp_tau_m, this);
  double tmp_tau_syn_inh = get_tau_syn_inh();
  nest::updateValueParam<double>(__d, nest::iaf_psc_exp_neuron_names::_tau_syn_inh, tmp_tau_syn_inh, this);
  double tmp_tau_syn_exc = get_tau_syn_exc();
  nest::updateValueParam<double>(__d, nest::iaf_psc_exp_neuron_names::_tau_syn_exc, tmp_tau_syn_exc, this);
  double tmp_refr_T = get_refr_T();
  nest::updateValueParam<double>(__d, nest::iaf_psc_exp_neuron_names::_refr_T, tmp_refr_T, this);
  double tmp_E_L = get_E_L();
  nest::updateValueParam<double>(__d, nest::iaf_psc_exp_neuron_names::_E_L, tmp_E_L, this);
  double tmp_V_reset = get_V_reset();
  nest::updateValueParam<double>(__d, nest::iaf_psc_exp_neuron_names::_V_reset, tmp_V_reset, this);
  double tmp_V_th = get_V_th();
  nest::updateValueParam<double>(__d, nest::iaf_psc_exp_neuron_names::_V_th, tmp_V_th, this);
  double tmp_I_e = get_I_e();
  nest::updateValueParam<double>(__d, nest::iaf_psc_exp_neuron_names::_I_e, tmp_I_e, this);

  // initial values for state variables in ODE or kernel
  double tmp_V_m = get_V_m();
  nest::updateValueParam<double>(__d, nest::iaf_psc_exp_neuron_names::_V_m, tmp_V_m, this);
  double tmp_refr_t = get_refr_t();
  nest::updateValueParam<double>(__d, nest::iaf_psc_exp_neuron_names::_refr_t, tmp_refr_t, this);
  double tmp_I_syn_exc = get_I_syn_exc();
  nest::updateValueParam<double>(__d, nest::iaf_psc_exp_neuron_names::_I_syn_exc, tmp_I_syn_exc, this);
  double tmp_I_syn_inh = get_I_syn_inh();
  nest::updateValueParam<double>(__d, nest::iaf_psc_exp_neuron_names::_I_syn_inh, tmp_I_syn_inh, this);

  // We now know that (ptmp, stmp) are consistent. We do not
  // write them back to (P_, S_) before we are also sure that
  // the properties to be set in the parent class are internally
  // consistent.
  ArchivingNode::set_status(__d);

  // if we get here, temporaries contain consistent set of properties
  set_C_m(tmp_C_m);
  set_tau_m(tmp_tau_m);
  set_tau_syn_inh(tmp_tau_syn_inh);
  set_tau_syn_exc(tmp_tau_syn_exc);
  set_refr_T(tmp_refr_T);
  set_E_L(tmp_E_L);
  set_V_reset(tmp_V_reset);
  set_V_th(tmp_V_th);
  set_I_e(tmp_I_e);
  set_V_m(tmp_V_m);
  set_refr_t(tmp_refr_t);
  set_I_syn_exc(tmp_I_syn_exc);
  set_I_syn_inh(tmp_I_syn_inh);





  // recompute internal variables in case they are dependent on parameters or state that might have been updated in this call to set_status()
  recompute_internal_variables();
};



#endif /* #ifndef IAF_PSC_EXP_NEURON */

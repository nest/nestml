/*
*  ${neuronName}.h
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
*/
#ifndef ${neuronName?upper_case}
#define ${neuronName?upper_case}
<#-- TODO make it depend on the ODE declaration -->
#include "config.h"

<#if useGSL>
#ifdef HAVE_GSL
#include <gsl/gsl_errno.h>
#include <gsl/gsl_matrix.h>
#include <gsl/gsl_odeiv.h>
// forwards the declaration of the function
extern "C" inline int ${neuronName}_dynamics( double, const double y[], double f[], void* pnode );
</#if>

// Includes from nestkernel:
#include "archiving_node.h"
#include "connection.h"
#include "event.h"
#include "nest_types.h"
#include "ring_buffer.h"
#include "universal_data_logger.h"


// Includes from sli:
#include "dictdatum.h"

/* BeginDocumentation
Name: ${neuronName}.

${neuronSymbol.printComment()}

Parameters:

Remarks:
Empty

References:
Empty

Sends: ${outputEvent}

Receives: <#if isSpikeInput>Spike, </#if><#if isCurrentInput>Current, </#if> DataLoggingRequest

SeeAlso:

Empty
*/
class ${neuronName} : public nest::Archiving_Node
{
public:
  /**
  * The constructor is only used to create the model prototype in the model manager.
  */
  ${neuronName}();

  /**
  * The copy constructor is used to create model copies and instances of the model.
  * @node The copy constructor needs to initialize the parameters and the state.
  *       Initialization of buffers and interal variables is deferred to
  *       @c init_buffers_() and @c calibrate().
  */
  ${neuronName}(const ${neuronName}&);

  /**
  * Releases resources.
  */
  ~${neuronName}();
  /**
  * Import sets of overloaded virtual functions.
  * This is necessary to ensure proper overload and overriding resolution.
  * @see http://www.gotw.ca/gotw/005.htm.
  */
  using nest::Node::handles_test_event;
  using nest::Node::handle;

  <#if isOutputEventPresent>
  /**
  * Used to validate that we can send ${outputEvent} to desired target:port.
  */
  nest::port send_test_event(nest::Node& target, nest::rport receptor_type, nest::synindex, bool);
  </#if>

  /**
  * @defgroup mynest_handle Functions handling incoming events.
  * We tell nest that we can handle incoming events of various types by
  * defining @c handle() and @c connect_sender() for the given event.
  * @{
  */
  <#if isSpikeInput>
  void handle(nest::SpikeEvent &);        //! accept spikes
  </#if>
  <#if isCurrentInput>
  void handle(nest::CurrentEvent &);      //! accept input current
  </#if>
  void handle(nest::DataLoggingRequest &);//! allow recording with multimeter

  <#if isSpikeInput>
  nest::port handles_test_event(nest::SpikeEvent&, nest::port);
  </#if>
  <#if isCurrentInput>
  nest::port handles_test_event(nest::CurrentEvent&, nest::port);
  </#if>
  nest::port handles_test_event(nest::DataLoggingRequest&, nest::port);
  /** @} */

  // SLI communication functions:
  void get_status(DictionaryDatum &) const;
  void set_status(const DictionaryDatum &);

private:

  <#if (body.getMultipleReceptors()?size > 1) >
    /**
     * Synapse types to connect to
     * @note Excluded upper and lower bounds are defined as INF_, SUP_.
     *       Excluding port 0 avoids accidental connections.
     */
    enum SynapseTypes
    {
      INF_SPIKE_RECEPTOR = 0,
      <#list body.getMultipleReceptors() as buffer>
        ${buffer.getName()?upper_case} ,
      </#list>
      SUP_SPIKE_RECEPTOR
    };
  </#if>
  //! Reset parameters and state of neuron.

  //! Reset state of neuron.
  void init_state_(const Node& proto);

  //! Reset internal buffers of neuron.
  void init_buffers_();

  //! Initialize auxiliary quantities, leave parameters and state untouched.
  void calibrate();

  //! Take neuron through given time interval
  void update(nest::Time const &, const long, const long);

  // The next two classes need to be friends to access the State_ class/member
  friend class nest::RecordablesMap<${neuronName}>;
  friend class nest::UniversalDataLogger<${neuronName}>;

  /**
  * Free parameters of the neuron.
  *
  * ${body.printParameterComment()}
  *
  * These are the parameters that can be set by the user through @c SetStatus.
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
  */
  struct Parameters_
  {
    <#list body.getParameterNonAliasSymbols() as variable>
      ${tc.includeArgs("org.nest.nestml.neuron.function.MemberDeclaration", [variable])}
    </#list>

    /** Initialize parameters to their default values. */
    Parameters_();
  };

  /**
  * Dynamic state of the neuron.
  *
  * ${body.printStateComment()}
  *
  * These are the state variables that are advanced in time by calls to
  * @c update(). In many models, some or all of them can be set by the user
  * through @c SetStatus. The state variables are initialized from the model
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
  */
  struct State_
  {
    <#if !useGSL>
      <#list body.getStateNonAliasSymbols() as variable>
        ${tc.includeArgs("org.nest.nestml.neuron.function.MemberDeclaration", [variable])}
      </#list>
    <#else>
      //! Symbolic indices to the elements of the state vector y
      enum StateVecElems
      {
        <#list body.getStateNonAliasSymbols() as variable>
          ${names.convertToCPPName(variable.getName())},
        </#list>
        STATE_VEC_SIZE
      };
      //! state vector, must be C-array for GSL solver
      double y[ STATE_VEC_SIZE ];
    </#if>

    <#list body.getODEAliases() as odeAlias>
      ${tc.includeArgs("org.nest.nestml.neuron.function.MemberDeclaration", [odeAlias])}
    </#list>

    State_();
  };

  /**
  * Internal variables of the neuron.
  *
  * ${body.printInternalComment()}
  *
  * These variables must be initialized by @c calibrate, which is called before
  * the first call to @c update() upon each call to @c Simulate.
  * @node Variables_ needs neither constructor, copy constructor or assignment operator,
  *       since it is initialized by @c calibrate(). If Variables_ has members that
  *       cannot destroy themselves, Variables_ will need a destructor.
  */
  struct Variables_ {
    <#list body.getInternalNonAliasSymbols() as variable>
      ${tc.includeArgs("org.nest.nestml.neuron.function.MemberDeclaration", [variable])}
    </#list>
  };

  /**
    * Buffers of the neuron.
    * Ususally buffers for incoming spikes and data logged for analog recorders.
    * Buffers must be initialized by @c init_buffers_(), which is called before
    * @c calibrate() on the first call to @c Simulate after the start of NEST,
    * ResetKernel or ResetNetwork.
    * @node Buffers_ needs neither constructor, copy constructor or assignment operator,
    *       since it is initialized by @c init_nodes_(). If Buffers_ has members that
    *       cannot destroy themselves, Buffers_ will need a destructor.
    */
  struct Buffers_ {
    Buffers_(${neuronName}&);
    Buffers_(const Buffers_ &, ${neuronName}&);

    /** Logger for all analog data */
    nest::UniversalDataLogger<${neuronName}> logger_;
    <#if (body.getMultipleReceptors()?size > 1) || body.isArrayBuffer()>
      std::vector<long> receptor_types_;
    </#if>

    <#if (body.getMultipleReceptors()?size > 1) >
      /** buffers and sums up incoming spikes/currents */
      std::vector< nest::RingBuffer > spike_inputs_;

      <#list body.getSpikeBuffers() as inputLine>
        ${bufferHelper.printBufferArrayGetter(inputLine)}
        ${bufferHelper.printBufferDeclarationValue(inputLine)};
      </#list>

    <#else>
      <#list body.getSpikeBuffers() as inputLine>
        ${bufferHelper.printBufferGetter(inputLine, true)}
        ${bufferHelper.printBufferDeclaration(inputLine)};
        ${bufferHelper.printBufferDeclarationValue(inputLine)};
      </#list>

    </#if>

    <#list body.getCurrentBuffers() as inputLine>
      ${bufferHelper.printBufferDeclaration(inputLine)};
      ${bufferHelper.printBufferGetter(inputLine, true)}
      ${bufferHelper.printBufferDeclarationValue(inputLine)};
    </#list>

    <#if useGSL>
      /** GSL ODE stuff */
      gsl_odeiv_step* __s;    //!< stepping function
      gsl_odeiv_control* __c; //!< adaptive stepsize control function
      gsl_odeiv_evolve* __e;  //!< evolution function
      gsl_odeiv_system __sys; //!< struct describing system

      // IntergrationStep_ should be reset with the neuron on ResetNetwork,
      // but remain unchanged during calibration. Since it is initialized with
      // step_, and the resolution cannot change after nodes have been created,
      // it is safe to place both here.
      double __step;             //!< step size in ms
      double __integration_step; //!< current integration time step, updated by GSL
    </#if>
  };

  <#list body.getStateSymbols() as state>
    ${tc.includeArgs("org.nest.nestml.neuron.function.MemberVariableGetterSetter", [state])}
  </#list>

  <#list body.getParameterSymbols() as parameter>
    ${tc.includeArgs("org.nest.nestml.neuron.function.MemberVariableGetterSetter", [parameter])}
  </#list>

  <#list body.getInternalSymbols() as internal>
    ${tc.includeArgs("org.nest.nestml.neuron.function.MemberVariableGetterSetter", [internal])}
  </#list>

  <#list body.getODEAliases() as odeAlias>
      ${tc.includeArgs("org.nest.nestml.neuron.function.MemberVariableGetterSetter", [odeAlias])}
  </#list>

  <#list body.getInputBuffers() as buffer>
    ${bufferHelper.printBufferGetter(buffer, false)};
  </#list>

  // Generate function header
  <#list body.getFunctions() as function>
  ${functionPrinter.printFunctionDeclaration(function)} ;
  </#list>
  /**
  * @defgroup pif_members Member variables of neuron model.
  * Each model neuron should have precisely the following four data members,
  * which are one instance each of the parameters, state, buffers and variables
  * structures. Experience indicates that the state and variables member should
  * be next to each other to achieve good efficiency (caching).
  * @note Devices require one additional data member, an instance of the @c Device
  *       child class they belong to.
  * @{
  */
  Parameters_ P_;  //!< Free parameters.
  State_      S_;  //!< Dynamic state.
  Variables_  V_;  //!< Internal Variables
  Buffers_    B_;  //!< Buffers.

  //! Mapping of recordables names to access functions
  static nest::RecordablesMap<${neuronName}> recordablesMap_;

  <#if useGSL>
    friend int ${neuronName}_dynamics( double, const double y[], double f[], void* pnode );
  </#if>
/** @} */
}; /* neuron ${neuronName} */

<#if isOutputEventPresent>
inline
nest::port ${neuronName}::send_test_event(nest::Node& target, nest::rport receptor_type, nest::synindex, bool)
{
  // You should usually not change the code in this function.
  // It confirms that the target of connection @c c accepts @c ${outputEvent} on
  // the given @c receptor_type.
  ${outputEvent} e;
  e.set_sender(*this);

  return target.handles_test_event(e, receptor_type);
}
</#if>


<#if isSpikeInput>
inline
nest::port ${neuronName}::handles_test_event(nest::SpikeEvent&, nest::port receptor_type)
{
  <#if neuronSymbol.isMultisynapseSpikes()>
    if ( receptor_type <= 0 || receptor_type > static_cast< nest::port >( get_${neuronSymbol.getSpikeBuffers()[0].getVectorParameter().get()}()) ) {
        // TODO refactor me. The code assumes that there is only one. Check by coco.
        throw nest::IncompatibleReceptorType( receptor_type, get_name(), "SpikeEvent" );
    }

    return receptor_type;
  <#elseif (body.getMultipleReceptors()?size > 1)>
    assert( B_.spike_inputs_.size() == ${body.getMultipleReceptors()?size } );

    if ( !( INF_SPIKE_RECEPTOR < receptor_type && receptor_type < SUP_SPIKE_RECEPTOR ) )
    {
      throw nest::UnknownReceptorType( receptor_type, get_name() );
      return 0;
    }
    else {
      return receptor_type - 1;
    }
  <#else>
    // You should usually not change the code in this function.
    // It confirms to the connection management system that we are able
    // to handle @c SpikeEvent on port 0. You need to extend the function
    // if you want to differentiate between input ports.
    if (receptor_type != 0)
      throw nest::UnknownReceptorType(receptor_type, get_name());
    return 0;
  </#if>

}
</#if>

<#if isCurrentInput>
inline
nest::port ${neuronName}::handles_test_event(nest::CurrentEvent&, nest::port receptor_type)
{
  // You should usually not change the code in this function.
  // It confirms to the connection management system that we are able
  // to handle @c CurrentEvent on port 0. You need to extend the function
  // if you want to differentiate between input ports.
  if (receptor_type != 0)
  throw nest::UnknownReceptorType(receptor_type, get_name());
  return 0;
}
</#if>
inline
nest::port ${neuronName}::handles_test_event(nest::DataLoggingRequest& dlr,
nest::port receptor_type)
{
  // You should usually not change the code in this function.
  // It confirms to the connection management system that we are able
  // to handle @c DataLoggingRequest on port 0.
  // The function also tells the built-in UniversalDataLogger that this node
  // is recorded from and that it thus needs to collect data during simulation.
  if (receptor_type != 0)
  throw nest::UnknownReceptorType(receptor_type, get_name());

  return B_.logger_.connect_logging_device(dlr, recordablesMap_);
}

// TODO call get_status on used or internal components
inline
void ${neuronName}::get_status(DictionaryDatum &__d) const
{
  <#list body.getParameterSymbols() as parameter>
  ${tc.includeArgs("org.nest.nestml.neuron.function.WriteInDictionary", [parameter])}
  </#list>
  <#list body.getStateSymbols() as state>
    ${tc.includeArgs("org.nest.nestml.neuron.function.WriteInDictionary", [state])}
  </#list>


  // TODO: ${body.getMultipleReceptors()?size}
  <#if (body.getMultipleReceptors()?size > 1) >

    DictionaryDatum __receptor_type = new Dictionary();
    <#list body.getMultipleReceptors() as spikeBuffer>
    ( *__receptor_type )[ "${spikeBuffer.getName()}" ] = ${spikeBuffer.getName()?upper_case};
    </#list>
    ( *__d )[ "receptor_types" ] = __receptor_type;
  </#if>

  (*__d)[nest::names::recordables] = recordablesMap_.get_list();
}

inline
void ${neuronName}::set_status(const DictionaryDatum &__d)
{
  <#list body.getParameterSymbols() as parameter>
  ${tc.includeArgs("org.nest.nestml.neuron.function.ReadFromDictionaryToTmp", [parameter])}
  </#list>

  <#list body.getStateSymbols() as state>
  ${tc.includeArgs("org.nest.nestml.neuron.function.ReadFromDictionaryToTmp", [state])}
  </#list>

  // We now know that (ptmp, stmp) are consistent. We do not
  // write them back to (P_, S_) before we are also sure that
  // the properties to be set in the parent class are internally
  // consistent.
  Archiving_Node::set_status(__d);

  // if we get here, temporaries contain consistent set of properties
  <#list body.getParameterSymbols() as parameter>
    ${tc.includeArgs("org.nest.nestml.neuron.function.AssignTmpDictionaryValue", [parameter])}
  </#list>

  <#list body.getStateSymbols() as state>
    ${tc.includeArgs("org.nest.nestml.neuron.function.AssignTmpDictionaryValue", [state])}
  </#list>
  <#list body.getParameterInvariants() as invariant>
    if ( !(${printerWithGetters.print(invariant)}) ) {
      throw nest::BadProperty("The constraint '${idemPrinter.print(invariant)}' is violated!");
    }
  </#list>
};

#endif /* #ifndef ${neuronName?upper_case} */
<#if useGSL>
#endif /* HAVE GSL */
</#if>
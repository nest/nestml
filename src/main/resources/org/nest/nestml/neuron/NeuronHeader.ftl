<#--
  @param ast ASTNeuron
  @param tc templatecontroller
  @result CPP Class
-->

/*
*  ${simpleNeuronName}.h
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


#ifndef ${simpleNeuronName?upper_case}
#define ${simpleNeuronName?upper_case}
<#-- TODO make it depend on the ODE declaration -->
#include "config.h"

<#if useGSL>
#ifdef HAVE_GSL
#include <gsl/gsl_errno.h>
#include <gsl/gsl_matrix.h>
#include <gsl/gsl_odeiv.h>
// forwards the declaration of the function
extern "C" inline int ${simpleNeuronName}_dynamics( double, const double y[], double f[], void* pnode );
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
Name: ${simpleNeuronName} .

${neuronSymbol.printComment()}

Parameters:

Remarks:
Empty

References:
Empty

Sends: ${outputEvent}

Receives: <#if isSpikeInput>Spike, </#if><#if isCurrentInput>Current, </#if>DataLoggingRequest


SeeAlso:
Empty
*/
class ${simpleNeuronName} : public nest::Archiving_Node
{
public:
  /**
  * The constructor is only used to create the model prototype in the model manager.
  */
  ${simpleNeuronName}();

  /**
  * The copy constructor is used to create model copies and instances of the model.
  * @node The copy constructor needs to initialize the parameters and the state.
  *       Initialization of buffers and interal variables is deferred to
  *       @c init_buffers_() and @c calibrate().
  */
  ${simpleNeuronName}(const ${simpleNeuronName}&);

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

  // Generate function header
  <#list body.getFunctions() as function>
  ${functionPrinter.printFunctionDeclaration(function)} ;
  </#list>

  <#list body.getStateSymbols() as state>
  ${tc.includeArgs("org.nest.nestml.function.MemberVariableGetterSetter", [state])}
  </#list>

  <#list body.getParameterSymbols() as parameter>
  ${tc.includeArgs("org.nest.nestml.function.MemberVariableGetterSetter", [parameter])}
  </#list>

  <#list body.getInternalSymbols() as internal>
  ${tc.includeArgs("org.nest.nestml.function.MemberVariableGetterSetter", [internal])}
  </#list>

  <#list body.getODEAliases() as odeAlias>
    ${tc.includeArgs("org.nest.nestml.function.MemberVariableGetterSetter", [odeAlias])}
  </#list>

  <#list body.getInputBuffers() as buffer>
  ${bufferHelper.printBufferGetter(buffer, false)};
  </#list>

protected:

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
  friend class nest::RecordablesMap<${simpleNeuronName}>;
  friend class nest::UniversalDataLogger<${simpleNeuronName}>;

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
      ${tc.includeArgs("org.nest.nestml.function.MemberDeclaration", [variable])}
    </#list>

    <#list body.getAllRelativeParameters() as variable>
      ${tc.includeArgs("org.nest.nestml.function.MemberDeclaration", [variable])}
    </#list>

    /** Initialize parameters to their default values. */
    Parameters_();

    /** Store parameter values in dictionary. */
    void get(DictionaryDatum&) const;

    /** Set parameter values from dictionary. */
    void set(const DictionaryDatum&
    <#list body.getAllOffsetVariables() as offset>
      , ${declarations.printVariableType(offset)} ${offset.getName()}
    </#list>);

    // TODO only for invariants
    <#list body.getParameterNonAliasSymbols() as variable>
      ${tc.includeArgs("org.nest.nestml.function.StructGetterSetter", [variable])}
    </#list>
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
    <#list body.getStateNonAliasSymbols() as variable>
      ${tc.includeArgs("org.nest.nestml.function.MemberDeclaration", [variable])}
    </#list>
    <#list body.getODEAliases() as odeAlias>
      ${tc.includeArgs("org.nest.nestml.function.MemberDeclaration", [odeAlias])}
    </#list>

    State_();

    /** Store state values in dictionary. */
    void get(DictionaryDatum&) const;

    /**
    * Set state values from dictionary.
    */
    void set(const DictionaryDatum&,
             const Parameters_&
    <#list body.getAllOffsetVariables() as offset>
      , ${declarations.printVariableType(offset)} ${offset.getName()}
    </#list>
    );
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
      ${tc.includeArgs("org.nest.nestml.function.MemberDeclaration", [variable])}
    </#list>

    <#list body.getInternalNonAliasSymbols() as variable>
      ${tc.includeArgs("org.nest.nestml.function.StructGetterSetter", [variable])}
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
    Buffers_(${simpleNeuronName}&);
    Buffers_(const Buffers_ &, ${simpleNeuronName}&);
    <#if (body.getSameTypeBuffer()?size > 1) >
      /** buffers and sums up incoming spikes/currents */
      std::vector< nest::RingBuffer > spike_inputs_;

      <#list body.getInputBuffers() as inputLine>
        ${bufferHelper.printBufferArrayGetter(inputLine)}
        ${bufferHelper.printBufferDeclaration(inputLine)};
      </#list>
    <#else>
      <#list body.getInputBuffers() as inputLine>
        ${bufferHelper.printBufferGetter(inputLine, true)}
        ${bufferHelper.printBufferDeclaration(inputLine)};
        ${bufferHelper.printBufferDeclarationValue(inputLine)};
      </#list>

    </#if>

    /** Logger for all analog data */
    nest::UniversalDataLogger<${simpleNeuronName}> logger_;

    std::vector<long> receptor_types_;

    <#if useGSL>
      /* GSL ODE stuff */
      gsl_odeiv_step* s_;    //!< stepping function
      gsl_odeiv_control* c_; //!< adaptive stepsize control function
      gsl_odeiv_evolve* e_;  //!< evolution function
      gsl_odeiv_system sys_; //!< struct describing system
    </#if>

  };
private:

  <#if (body.getSameTypeBuffer()?size > 1) >
    /**
     * Synapse types to connect to
     * @note Excluded upper and lower bounds are defined as INF_, SUP_.
     *       Excluding port 0 avoids accidental connections.
     */
    enum SynapseTypes
    {
      INF_SPIKE_RECEPTOR = 0,
      <#list body.getSameTypeBuffer() as buffer>
        ${buffer.getName()?upper_case} ,
      </#list>
      SUP_SPIKE_RECEPTOR
    };
  </#if>

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
  static nest::RecordablesMap<${simpleNeuronName}> recordablesMap_;

  <#if useGSL>
    friend int ${simpleNeuronName}_dynamics( double, const double y[], double f[], void* pnode );
  </#if>
/** @} */
}; /* neuron ${simpleNeuronName} */

<#if isOutputEventPresent>
inline
nest::port ${simpleNeuronName}::send_test_event(nest::Node& target, nest::rport receptor_type, nest::synindex, bool)
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
nest::port ${simpleNeuronName}::handles_test_event(nest::SpikeEvent&, nest::port receptor_type)
{

  <#if neuronSymbol.isMultisynapseSpikes()>
    if ( receptor_type <= 0 || receptor_type > static_cast< nest::port >( get_${neuronSymbol.getSpikeBuffers()[0].getVectorParameter().get()}()) ) {
        // TODO refactor me. The code assumes that there is only one. Check by coco.
        throw nest::IncompatibleReceptorType( receptor_type, get_name(), "SpikeEvent" );
    }

    return receptor_type;
  <#elseif (body.getSameTypeBuffer()?size > 1)>
    assert( B_.spike_inputs_.size() == ${body.getSameTypeBuffer()?size } );

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
nest::port ${simpleNeuronName}::handles_test_event(nest::CurrentEvent&, nest::port receptor_type)
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
nest::port ${simpleNeuronName}::handles_test_event(nest::DataLoggingRequest& dlr,
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
void ${simpleNeuronName}::get_status(DictionaryDatum &__d) const
{
  P_.get(__d);
  <#list body.getParameterSymbols() as parameter>
  ${tc.includeArgs("org.nest.nestml.function.WriteInDictionary", [parameter])}
  </#list>
  S_.get(__d);
  <#list body.getStateSymbols() as state>
    ${tc.includeArgs("org.nest.nestml.function.WriteInDictionary", [state])}
  </#list>

  <#if (body.getSameTypeBuffer()?size > 1) >

    DictionaryDatum __receptor_type = new Dictionary();
    <#list body.getSameTypeBuffer() as spikeBuffer>
    ( *__receptor_type )[ "${spikeBuffer.getName()?upper_case}" ] = ${spikeBuffer.getName()?upper_case};
    </#list>
    ( *__d )[ "receptor_types" ] = __receptor_type;
  </#if>

  (*__d)[nest::names::recordables] = recordablesMap_.get_list();
}

inline
void ${simpleNeuronName}::set_status(const DictionaryDatum &__d)
{
  <#list body.getAllOffsetVariables() as offset>
    ${tc.includeArgs("org.nest.nestml.function.StoreDeltaValue", [offset])}
  </#list>

  Parameters_ ptmp = P_;  // temporary copy in case of errors
  ptmp.set(__d
  <#list body.getAllOffsetVariables() as offset>
    , delta_${offset.getName()}
  </#list>
  );            // throws BadProperty

  State_      stmp = S_;  // temporary copy in case of errors
  stmp.set(__d, ptmp
  <#list body.getAllOffsetVariables() as offset>
    , delta_${offset.getName()}
  </#list>
  );            // throws BadProperty

  // We now know that (ptmp, stmp) are consistent. We do not
  // write them back to (P_, S_) before we are also sure that
  // the properties to be set in the parent class are internally
  // consistent.
  Archiving_Node::set_status(__d);

  // if we get here, temporaries contain consistent set of properties
  P_ = ptmp;
  S_ = stmp;
};

#endif /* #ifndef ${simpleNeuronName?upper_case} */
<#if useGSL>
#endif /* HAVE GSL */
</#if>
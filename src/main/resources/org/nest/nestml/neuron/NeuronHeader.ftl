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

<#if neuronSymbol.getBaseNeuron().isPresent()>
#include "${neuronSymbol.getBaseNeuron().get().getName()}.h"
</#if>

<#if useGSL>
#ifdef HAVE_GSL
#include <gsl/gsl_errno.h>
#include <gsl/gsl_matrix.h>
#include <gsl/gsl_odeiv.h>
</#if>

#include "nest.h"
#include "event.h"
#include "archiving_node.h"
#include "connection.h"
#include "universal_data_logger.h"
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
class ${simpleNeuronName}
<#if neuronSymbol.getBaseNeuron().isPresent()>
: public ${neuronSymbol.getBaseNeuron().get().getName()}
<#else>
: public nest::Archiving_Node
</#if>

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

  <#list body.getInputLines() as inputLine>
  ${bufferHelper.printBufferGetter(inputLine, false)};
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
  void update(nest::Time const &, const nest::long_t, const nest::long_t);

  // The next two classes need to be friends to access the State_ class/member
  friend class nest::RecordablesMap<${simpleNeuronName}>;
  friend class nest::UniversalDataLogger<${simpleNeuronName}>;

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
  struct State_ <#if neuronSymbol.getBaseNeuron().isPresent()> : ${neuronSymbol.getBaseNeuron().get().getName()}::State_ </#if> {
    <#list body.getStateNonAliasSymbols() as variable>
    ${tc.includeArgs("org.nest.nestml.function.MemberDeclaration", [variable])}
    </#list>
    State_();

    /** Store state values in dictionary. */
    void get(DictionaryDatum&) const;

    /**
    * Set state values from dictionary.
    */
    void set(const DictionaryDatum&);

    <#list body.getStateNonAliasSymbols() as variable>
    ${tc.includeArgs("org.nest.nestml.function.StructGetterSetter", [variable])}
    </#list>
  };

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
  struct Parameters_ <#if neuronSymbol.getBaseNeuron().isPresent()> : ${neuronSymbol.getBaseNeuron().get().getName()}::Parameters_ </#if>
  {
    <#list body.getParameterNonAliasSymbols() as variable>
      ${tc.includeArgs("org.nest.nestml.function.MemberDeclaration", [variable])}
    </#list>
    /** Initialize parameters to their default values. */
    Parameters_();

    /** Store parameter values in dictionary. */
    void get(DictionaryDatum&) const;

    /** Set parameter values from dictionary. */
    void set(const DictionaryDatum&);

    <#list body.getParameterNonAliasSymbols() as variable>
      ${tc.includeArgs("org.nest.nestml.function.StructGetterSetter", [variable])}
    </#list>
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
  struct Variables_ <#if neuronSymbol.getBaseNeuron().isPresent()> : ${neuronSymbol.getBaseNeuron().get().getName()}::Variables_ </#if> {
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
  struct Buffers_ <#if neuronSymbol.getBaseNeuron().isPresent()> : ${neuronSymbol.getBaseNeuron().get().getName()}::Buffers_ </#if> {
    Buffers_(${simpleNeuronName}&);
    Buffers_(const Buffers_ &, ${simpleNeuronName}&);
    <#list body.getInputLines() as inputLine>
      ${bufferHelper.printBufferGetter(inputLine, true)}
    </#list>

    /** Logger for all analog data */
    nest::UniversalDataLogger<${simpleNeuronName}> logger_;

    <#list body.getInputLines() as inputLine>
      ${bufferHelper.printBufferDeclaration(inputLine)};
    </#list>

    <#list body.getInputLines() as inputLine>
      ${bufferHelper.printBufferTypesVariables(inputLine)};
    </#list>

    <#if useGSL>
    /* GSL ODE stuff */
    gsl_odeiv_step* s_;    //!< stepping function
    gsl_odeiv_control* c_; //!< adaptive stepsize control function
    gsl_odeiv_evolve* e_;  //!< evolution function
    gsl_odeiv_system sys_; //!< struct describing system
    </#if>


  };
private:
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
  // You should usually not change the code in this function.
  // It confirms to the connection management system that we are able
  // to handle @c SpikeEvent on port 0. You need to extend the function
  // if you want to differentiate between input ports.
  if (receptor_type != 0)
  throw nest::UnknownReceptorType(receptor_type, get_name());
  return 0;
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
void ${simpleNeuronName}::get_status(DictionaryDatum &d) const
{
  P_.get(d);
  <#list body.getParameterSymbols() as parameter>
  ${tc.includeArgs("org.nest.nestml.function.WriteInDictionary", [parameter])}
  </#list>
  S_.get(d);
  <#list body.getStateAliasSymbols() as state>
    ${tc.includeArgs("org.nest.nestml.function.WriteInDictionary", [state])}
  </#list>

  (*d)[nest::names::recordables] = recordablesMap_.get_list();
}

// TODO call set_status on used or internal components
inline
void ${simpleNeuronName}::set_status(const DictionaryDatum &d)
{
  <#list body.getParameterAliasSymbols() as parameter>
    ${tc.includeArgs("org.nest.nestml.function.SetOldAliasState", [parameter])}
  </#list>
  <#list body.getStateAliasSymbols() as state>
    ${tc.includeArgs("org.nest.nestml.function.SetOldAliasState", [state])}
  </#list>

  Parameters_ ptmp = P_;  // temporary copy in case of errors
  ptmp.set(d);            // throws if BadProperty

  // alias setter-functions perform the set on the member-variable P_, hence
  // we swap ptmp and P_ and 're-swap' afterwards.
  std::swap(P_, ptmp);

  <#list body.getParameterAliasSymbols() as parameter>
  ${tc.includeArgs("org.nest.nestml.function.ReadFromDictionary", [parameter])}
  </#list>

  State_      stmp = S_;  // temporary copy in case of errors
  stmp.set(d);            // throws if BadProperty

  // alias setter-functions perform the set on the member-variable S_, hence
  // we swap stmp and S_ and 're-swap' afterwards.
  // P_ and ptmp stay swaped, since the alias might access parameters
  std::swap(S_, stmp);
  <#list body.getStateAliasSymbols() as state>
  ${tc.includeArgs("org.nest.nestml.function.ReadFromDictionary", [state])}
  </#list>
  // 're-swap' when everything is ok (TODO: check for tests)
  std::swap(P_, ptmp);
  std::swap(S_, stmp);

  // if we get here, temporaries contain consistent set of properties
  P_ = ptmp;
  S_ = stmp;
};

#endif /* #ifndef ${simpleNeuronName?upper_case} */
<#if useGSL>
#endif /* HAVE GSL */
</#if>
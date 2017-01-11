/*
*  ${ast.getName()}.cpp
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

// C++ includes:
#include <limits>

// Includes from libnestutil:
#include "numerics.h"

// Includes from nestkernel:
#include "exceptions.h"
#include "kernel_manager.h"
#include "universal_data_logger_impl.h"

// Includes from sli:
#include "dict.h"
#include "dictutils.h"
#include "doubledatum.h"
#include "integerdatum.h"
#include "lockptrdatum.h"

#include "${neuronName}.h"

<#assign stateSize = body.getEquations()?size>
/* ----------------------------------------------------------------
* Recordables map
* ---------------------------------------------------------------- */
nest::RecordablesMap<${neuronName}> ${neuronName}::recordablesMap_;

namespace nest
{
  // Override the create() method with one call to RecordablesMap::insert_()
  // for each quantity to be recorded.
  template <>
  void RecordablesMap<${neuronName}>::create()
  {
    // use standard names whereever you can for consistency!
    <#list body.getStateSymbols() as state>
      ${tc.includeArgs("org.nest.nestml.neuron.function.RecordCallback", [state])}
    </#list>
    <#list body.getInternalSymbols() as internal>
      ${tc.includeArgs("org.nest.nestml.neuron.function.RecordCallback", [internal])}
    </#list>
    <#list body.getParameterSymbols() as parameter>
      ${tc.includeArgs("org.nest.nestml.neuron.function.RecordCallback", [parameter])}
    </#list>
    <#list body.getODEAliases() as odeAlias>
      ${tc.includeArgs("org.nest.nestml.neuron.function.RecordCallback", [odeAlias])}
    </#list>
  }

}

/* ----------------------------------------------------------------
* Default constructors defining default parameters and state
* ---------------------------------------------------------------- */
${neuronName}::Parameters_::Parameters_()
{
}

${neuronName}::State_::State_()
{
}

/* ----------------------------------------------------------------
* Parameter and state extractions and manipulation functions
* ---------------------------------------------------------------- */

${neuronName}::Buffers_::Buffers_(${ast.getName()} &n): logger_(n)
<#if (body.getMultipleReceptors()?size > 1) >
  , spike_inputs_( std::vector< nest::RingBuffer >( SUP_SPIKE_RECEPTOR - 1 ) )
</#if>
<#if useGSL>
  , __s( 0 )
  , __c( 0 )
  , __e( 0 )
</#if>
{

}

${neuronName}::Buffers_::Buffers_(const Buffers_ &, ${ast.getName()} &n): logger_(n)
<#if (body.getMultipleReceptors()?size > 1)>
  , spike_inputs_( std::vector< nest::RingBuffer >( SUP_SPIKE_RECEPTOR - 1 ) )
</#if>
<#if useGSL>
  , __s( 0 )
  , __c( 0 )
  , __e( 0 )
</#if>

{
}

/* ----------------------------------------------------------------
* Default and copy constructor for node
* ---------------------------------------------------------------- */
// TODO inner components
${neuronName}::${neuronName}():Archiving_Node(), P_(), S_(), B_(*this)
{
  recordablesMap_.create();

  <#list body.getParameterNonAliasSymbols() as parameter>
    ${tc.includeArgs("org.nest.nestml.neuron.function.MemberInitialization", [parameter, printerWithGetters])}
  </#list>

  <#list body.getStateNonAliasSymbols() as state>
    ${tc.includeArgs("org.nest.nestml.neuron.function.MemberInitialization", [state, printerWithGetters])}
  </#list>

}

${neuronName}::${neuronName}(const ${neuronName}& __n): Archiving_Node(), P_(__n.P_), S_(__n.S_), B_(__n.B_, *this)
{
  <#list body.getParameterNonAliasSymbols() as parameter>
    P_.${names.name(parameter)} = __n.P_.${names.name(parameter)};
  </#list>

  <#list body.getStateNonAliasSymbols() as state>
    S_.${names.name(state)} = __n.S_.${names.name(state)};
  </#list>

  <#list body.getInternalNonAliasSymbols() as internal>
    V_.${names.name(internal)} = __n.V_.${names.name(internal)};
  </#list>
}

/* ----------------------------------------------------------------
* Destructors
* ---------------------------------------------------------------- */

${neuronName}::~${neuronName}()
{
  <#if useGSL>
    // GSL structs may not have been allocated, so we need to protect destruction
    if ( B_.__s )
      gsl_odeiv_step_free( B_.__s );
    if ( B_.__c )
      gsl_odeiv_control_free( B_.__c );
    if ( B_.__e )
      gsl_odeiv_evolve_free( B_.__e );
  </#if>
}

/* ----------------------------------------------------------------
* Node initialization functions
* ---------------------------------------------------------------- */

void
${neuronName}::init_state_(const Node& proto)
{ // TODO inner components

  const ${ast.getName()}& pr = downcast<${ast.getName()}>(proto);
  S_ = pr.S_;
}

<#if useGSL>
${tc.include("org.nest.nestml.neuron.function.GSLDifferentiationFunction", body)}
</#if>

void
${neuronName}::init_buffers_()
{
  <#list body.getInputBuffers() as buffer>
  ${bufferHelper.printBufferInitialization(buffer)}
  </#list>
  B_.logger_.reset(); // includes resize
  Archiving_Node::clear_history();
  <#if useGSL>
    if ( B_.__s == 0 )
    {
      B_.__s = gsl_odeiv_step_alloc( gsl_odeiv_step_rkf45, ${stateSize} );
    }
    else
    {
      gsl_odeiv_step_reset( B_.__s );
    }

    if ( B_.__c == 0 )
    {
      B_.__c = gsl_odeiv_control_y_new( 1e-6, 0.0 );
    }
    else
    {
      gsl_odeiv_control_init( B_.__c, 1e-6, 0.0, 1.0, 0.0 );
    }

    if ( B_.__e == 0 )
    {
      B_.__e = gsl_odeiv_evolve_alloc( ${stateSize} );
    }
    else
    {
      gsl_odeiv_evolve_reset( B_.__e );
    }

    B_.__sys.function = ${neuronName}_dynamics;
    B_.__sys.jacobian = NULL;
    B_.__sys.dimension = ${stateSize};
    B_.__sys.params = reinterpret_cast< void* >( this );
    B_.__step = nest::Time::get_resolution().get_ms();
    B_.__integration_step = nest::Time::get_resolution().get_ms();
  </#if>

}

void
${neuronName}::calibrate()
{
  B_.logger_.init();

  <#list body.getInternalNonAliasSymbols() as variable>
    ${tc.includeArgs("org.nest.nestml.neuron.function.Calibrate", [variable])}
  </#list>

  <#list body.getStateNonAliasSymbols() as variable>
    <#if variable.isVector()>
      ${tc.includeArgs("org.nest.nestml.neuron.function.Calibrate", [variable])}
    </#if>
  </#list>

  <#list body.getInputBuffers() as buffer>
    <#if buffer.isVector()>
        B_.${buffer.getName()}.resize(P_.${buffer.getVectorParameter().get()});
        B_.${buffer.getName()}_last_value_.resize(P_.${buffer.getVectorParameter().get()});
    </#if>

  </#list>
}

/* ----------------------------------------------------------------
* Update and spike handling functions
* ---------------------------------------------------------------- */

/*
 ${body.printDynamicsComment()}
 */
void
${neuronName}::update(
        nest::Time const & origin,
        const long from, const long to)
{
    <#if useGSL>
      double t = 0;
    </#if>

    for ( long lag = from ; lag < to ; ++lag ) {
      <#list body.getInputBuffers() as inputLine>
         <#if inputLine.isVector()>
         for (long i=0; i < P_.${inputLine.getVectorParameter().get()}; i++)
         {
           B_.${names.bufferValue(inputLine)}[i] = get_${names.name(inputLine)}()[i].get_value( lag );
         }
         <#else>
         // TODO this case must be handled uniformly, also NESTReferenceConverter must be adopted
            B_.${names.bufferValue(inputLine)} = get_${names.name(inputLine)}().get_value( lag );
         </#if>
      </#list>

      <#assign dynamics = body.getDynamicsBlock().get()>
      ${tc.include("org.nest.spl.Block", dynamics.getBlock())}

      // voltage logging
      B_.logger_.record_data(origin.get_steps()+lag);
    }

}


// Do not move this function as inline to h-file. It depends on
// universal_data_logger_impl.h being included here.
void
${neuronName}::handle(nest::DataLoggingRequest& e)
{
    B_.logger_.handle(e);
}

<#list body.getFunctions() as function>
${functionPrinter.printFunctionDefinition(function, neuronName)}
{
  ${tc.include("org.nest.spl.Block", function.getBlock())}
}
</#list>

<#if isSpikeInput>
void
${neuronName}::handle(nest::SpikeEvent &e)
{
  assert(e.get_delay() > 0);

  <#if neuronSymbol.isMultisynapseSpikes()>
    <#assign spikeBuffer = neuronSymbol.getSpikeBuffers()[0]>

    B_.${spikeBuffer.getName()}[e.get_rport() - 1].add_value(
      e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin() ),
      e.get_weight() * e.get_multiplicity() );
  <#elseif (body.getMultipleReceptors()?size > 1)>
    assert( e.get_rport() < static_cast< int >( B_.spike_inputs_.size() ) );

    B_.spike_inputs_[ e.get_rport() ].add_value(
      e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin() ),
      e.get_weight() * e.get_multiplicity() );
  <#else>
      const double weight = e.get_weight();
      const double multiplicity = e.get_multiplicity();
      <#list body.getSpikeBuffers() as buffer>
        <#if buffer.isExcitatory()>
        if ( weight >= 0.0 ) // excitatory
        {
          get_${buffer.getName()}().add_value(e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin()),
                       weight * multiplicity );
        }
        </#if>
        <#if buffer.isInhibitory()>
        if ( weight < 0.0 ) // inhibitory
        {
          get_${buffer.getName()}().add_value(e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin()),
                      <#if buffer.isConductanceBased()> // ensure conductance is positive </#if>
                      <#if buffer.isConductanceBased()> -1 * </#if> weight * multiplicity );
        }
        </#if>
      </#list>

  </#if>
}
</#if>

<#if isCurrentInput>
void
${neuronName}::handle(nest::CurrentEvent& e)
{
  assert(e.get_delay() > 0);

  const double current=e.get_current();
  const double weight=e.get_weight();

  // add weighted current; HEP 2002-10-04
  <#list body.getCurrentBuffers() as buffer>
    get_${buffer.getName()}().add_value(
               e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin()),
               weight * current );
  </#list>
}
</#if>
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

#include "${simpleNeuronName}.h"

<#assign stateSize = body.getEquations()?size>
/* ----------------------------------------------------------------
* Recordables map
* ---------------------------------------------------------------- */
nest::RecordablesMap<${simpleNeuronName}> ${simpleNeuronName}::recordablesMap_;

namespace nest
{
  // Override the create() method with one call to RecordablesMap::insert_()
  // for each quantity to be recorded.
  template <>
  void RecordablesMap<${simpleNeuronName}>::create()
  {
    // use standard names whereever you can for consistency!
    <#list body.getStateSymbols() as state>
      ${tc.includeArgs("org.nest.nestml.function.RecordCallback", [state])}
    </#list>
    <#list body.getInternalSymbols() as internal>
      ${tc.includeArgs("org.nest.nestml.function.RecordCallback", [internal])}
    </#list>
    <#list body.getParameterSymbols() as parameter>
      ${tc.includeArgs("org.nest.nestml.function.RecordCallback", [parameter])}
    </#list>
    <#list body.getODEAliases() as odeAlias>
      ${tc.includeArgs("org.nest.nestml.function.RecordCallback", [odeAlias])}
    </#list>
  }

}

/* ----------------------------------------------------------------
* Default constructors defining default parameters and state
* ---------------------------------------------------------------- */

${simpleNeuronName}::Parameters_::Parameters_() { }

${simpleNeuronName}::State_::State_() { }

/* ----------------------------------------------------------------
* Parameter and state extractions and manipulation functions
* ---------------------------------------------------------------- */

void
${simpleNeuronName}::Parameters_::set(const DictionaryDatum& __d
<#list body.getAllOffsetVariables() as offset>
  , ${declarations.printVariableType(offset)} delta_${offset.getName()}
</#list>
)
{

  <#list body.getParameterSymbols() as parameter>
  ${tc.includeArgs("org.nest.nestml.function.ReadFromDictionary", [parameter])}
  </#list>

  ${tc.include("org.nest.nestml.function.Invariant", body.getParameterInvariants())}

}

void
${simpleNeuronName}::State_::set(const DictionaryDatum& __d, const Parameters_& p
<#list body.getAllOffsetVariables() as offset>
  , ${declarations.printVariableType(offset)} delta_${offset.getName()}
</#list>
)
{
  <#list body.getStateSymbols() as state>
  ${tc.includeArgs("org.nest.nestml.function.ReadFromDictionary", [state])}
  </#list>
}

${simpleNeuronName}::Buffers_::Buffers_(${ast.getName()} &n): logger_(n)
<#if useGSL>
  , s_( 0 )
  , c_( 0 )
  , e_( 0 )
</#if>
<#if (body.getSameTypeBuffer()?size > 1) >
  , spike_inputs_( std::vector< nest::RingBuffer >( SUP_SPIKE_RECEPTOR - 1 ) )
</#if>
{

}

${simpleNeuronName}::Buffers_::Buffers_(const Buffers_ &, ${ast.getName()} &n): logger_(n)
<#if useGSL>
  , s_( 0 )
  , c_( 0 )
  , e_( 0 )
</#if>
<#if (body.getSameTypeBuffer()?size > 1) >
  , spike_inputs_( std::vector< nest::RingBuffer >( SUP_SPIKE_RECEPTOR - 1 ) )
</#if>
{
}

/* ----------------------------------------------------------------
* Default and copy constructor for node
* ---------------------------------------------------------------- */
// TODO inner components
${simpleNeuronName}::${simpleNeuronName}():Archiving_Node(), P_(), S_(), B_(*this)
{
  recordablesMap_.create();

  <#list body.getParameterNonAliasSymbols() as parameter>
    ${tc.includeArgs("org.nest.nestml.function.MemberInitialization", [parameter, printerWithGetters])}
  </#list>

  <#list body.getAllRelativeParameters() as parameter>
    ${tc.includeArgs("org.nest.nestml.function.MemberInitialization", [parameter, printerWithGetters])}
  </#list>

  <#list body.getStateNonAliasSymbols() as state>
    ${tc.includeArgs("org.nest.nestml.function.MemberInitialization", [state, printerWithGetters])}
  </#list>

}

${simpleNeuronName}::${simpleNeuronName}(const ${simpleNeuronName}& n): Archiving_Node(), P_(n.P_), S_(n.S_), B_(n.B_, *this)
{}

/* ----------------------------------------------------------------
* Destructors
* ---------------------------------------------------------------- */

${simpleNeuronName}::~${simpleNeuronName}()
{
  <#if useGSL>
    // GSL structs may not have been allocated, so we need to protect destruction
    if ( B_.s_ )
      gsl_odeiv_step_free( B_.s_ );
    if ( B_.c_ )
      gsl_odeiv_control_free( B_.c_ );
    if ( B_.e_ )
      gsl_odeiv_evolve_free( B_.e_ );
  </#if>
}

/* ----------------------------------------------------------------
* Node initialization functions
* ---------------------------------------------------------------- */

void
${simpleNeuronName}::init_state_(const Node& proto)
{ // TODO inner components

  const ${ast.getName()}& pr = downcast<${ast.getName()}>(proto);
  S_ = pr.S_;
}

<#if useGSL>
${tc.include("org.nest.nestml.function.GSLDifferentiationFunction", body)}
</#if>

void
${simpleNeuronName}::init_buffers_()
{
  <#list body.getInputBuffers() as buffer>
  ${bufferHelper.printBufferInitialization(buffer)}
  </#list>
  B_.logger_.reset(); // includes resize
  Archiving_Node::clear_history();
  <#if useGSL>
    if ( B_.s_ == 0 )
    B_.s_ = gsl_odeiv_step_alloc( gsl_odeiv_step_rkf45, ${stateSize} );
    else
    gsl_odeiv_step_reset( B_.s_ );

    if ( B_.c_ == 0 ) {
      B_.c_ = gsl_odeiv_control_y_new( 1e-6, 0.0 );
    }
    else {
      gsl_odeiv_control_init( B_.c_, 1e-6, 0.0, 1.0, 0.0 );
    }

    if ( B_.e_ == 0 ) {
      B_.e_ = gsl_odeiv_evolve_alloc( ${stateSize} );
    }
    else {
      gsl_odeiv_evolve_reset( B_.e_ );
    }

    B_.sys_.function = ${simpleNeuronName}_dynamics;
    B_.sys_.jacobian = NULL;
    B_.sys_.dimension = ${stateSize};
    B_.sys_.params = reinterpret_cast< void* >( this );

  </#if>

}

void
${simpleNeuronName}::calibrate()
{
  B_.logger_.init();

  <#list body.getInternalNonAliasSymbols() as variable>
    ${tc.includeArgs("org.nest.nestml.function.Calibrate", [variable])}
  </#list>

  <#list body.getStateNonAliasSymbols() as variable>
    <#if variable.isVector()>
      ${tc.includeArgs("org.nest.nestml.function.Calibrate", [variable])}
    </#if>
  </#list>

  <#list body.getInputBuffers() as buffer>
    <#if buffer.isVector()>
        B_.${buffer.getName()}.resize(P_.${buffer.getVectorParameter().get()});
        B_.receptor_types_.resize(P_.${buffer.getVectorParameter().get()});
        for (long i=0; i < P_.${buffer.getVectorParameter().get()}; i++)
        {
          B_.receptor_types_[i] = i+1;
        }
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
${simpleNeuronName}::update(
        nest::Time const & origin,
        const long from, const long to)
{
    <#assign dynamics = body.getDynamicsBlock().get()>
    for ( long lag = from ; lag < to ; ++lag ) {
      <#list body.getInputBuffers() as inputLine>
         <#if !inputLine.isVector()>
           // TODO this case must be handled uniformly, also NESTReferenceConverter must be adopted
           B_.${names.bufferValue(inputLine)} = get_${names.name(inputLine)}().get_value( lag );
         </#if>
      </#list>

      ${tc.include("org.nest.spl.Block", dynamics.getBlock())}

      // voltage logging
      B_.logger_.record_data(origin.get_steps()+lag);
    }
}


// Do not move this function as inline to h-file. It depends on
// universal_data_logger_impl.h being included here.
void
${simpleNeuronName}::handle(nest::DataLoggingRequest& e)
{
    B_.logger_.handle(e);
}

<#list body.getFunctions() as function>
${functionPrinter.printFunctionDefinition(function, simpleNeuronName)}
{
  ${tc.include("org.nest.spl.Block", function.getBlock())}
}
</#list>

<#if isSpikeInput>
void
${simpleNeuronName}::handle(nest::SpikeEvent &e)
{
  assert(e.get_delay() > 0);

  <#if neuronSymbol.isMultisynapseSpikes()>
    <#assign spikeBuffer = neuronSymbol.getSpikeBuffers()[0]>

    for ( long i = 0; i < P_.${spikeBuffer.getVectorParameter().get()}; ++i )
      {
        if ( B_.receptor_types_[ i ] == e.get_rport() )
        {
            B_.${spikeBuffer.getName()}[i].add_value(
              e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin() ),
              e.get_weight() * e.get_multiplicity() );
        }
      }
  <#elseif (body.getSameTypeBuffer()?size > 1)>
    assert( e.get_rport() < static_cast< int >( B_.spike_inputs_.size() ) );

    B_.spike_inputs_[ e.get_rport() ].add_value(
      e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin() ),
      e.get_weight() * e.get_multiplicity() );
  <#else>
      const double weight = e.get_weight();
      const double multiplicity = e.get_multiplicity();
      <#list body.getSpikeBuffers() as buffer>
        ${tc.includeArgs("org.nest.nestml.buffer.SpikeBufferFill", [buffer])}
      </#list>

  </#if>
}
</#if>

<#if isCurrentInput>
void
${simpleNeuronName}::handle(nest::CurrentEvent& e)
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
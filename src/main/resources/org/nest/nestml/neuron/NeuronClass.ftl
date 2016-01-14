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

#include "exceptions.h"
#include "network.h"
#include "dict.h"
#include "integerdatum.h"
#include "doubledatum.h"
#include "dictutils.h"
#include "numerics.h"
#include "universal_data_logger_impl.h"

#include <limits>
<#assign stateSize = body.getNonAliasStates()?size>

// TODO it cannot work with several neurons
#include "${simpleNeuronName}.h"

/* ----------------------------------------------------------------
* Recordables map
* ---------------------------------------------------------------- */
nest::RecordablesMap<${nspPrefix}::${simpleNeuronName}> ${nspPrefix}::${simpleNeuronName}::recordablesMap_;

namespace nest
{
  // Override the create() method with one call to RecordablesMap::insert_()
  // for each quantity to be recorded.
  template <>
  void RecordablesMap<${nspPrefix}::${simpleNeuronName}>::create()
  {
    // use standard names whereever you can for consistency!
    <#list body.getStates() as state>
      ${tc.include("org.nest.nestml.function.RecordCallback", state)}
    </#list>
    <#list body.getInternals() as internal>
      ${tc.include("org.nest.nestml.function.RecordCallback", internal)}
    </#list>
    <#list body.getParameters() as parameter>
      ${tc.include("org.nest.nestml.function.RecordCallback", parameter)}
    </#list>
  }
}

/* ----------------------------------------------------------------
* Default constructors defining default parameters and state
* ---------------------------------------------------------------- */
<#assign start="">
${nspPrefix}::${simpleNeuronName}::Parameters_::Parameters_():
<#list body.getNonAliasParameters() as parameter>
  ${start} ${tc.include("org.nest.nestml.function.MemberInitialization", parameter)}
  <#assign start=",">
</#list>
{}

<#assign start="">
${nspPrefix}::${simpleNeuronName}::State_::State_():
<#list body.getNonAliasStates() as state>
  ${start} ${tc.include("org.nest.nestml.function.MemberInitialization", state)}
  <#assign start=",">
</#list>
{}

/* ----------------------------------------------------------------
* Parameter and state extractions and manipulation functions
* ---------------------------------------------------------------- */

void
${nspPrefix}::${simpleNeuronName}::Parameters_::get(DictionaryDatum &d) const
{
  <#list body.getNonAliasParameters() as parameter>
  ${tc.include("org.nest.nestml.function.WriteInDictionary", parameter)}
  </#list>
}

void
${nspPrefix}::${simpleNeuronName}::Parameters_::set(const DictionaryDatum& d)
{
  <#list body.getNonAliasParameters() as parameter>
  ${tc.include("org.nest.nestml.function.ReadFromDictionary", parameter)}
  </#list>

  <#list body.getNonAliasParameters() as parameter>
    <#list parameter.getInvariants() as invariant>
      ${tc.include("org.nest.nestml.function.Invariant", invariant)}
    </#list>
  </#list>

}

void
${nspPrefix}::${simpleNeuronName}::State_::get(DictionaryDatum &d) const
{
    <#list body.getNonAliasStates() as state>
    ${tc.include("org.nest.nestml.function.WriteInDictionary", state)}
    </#list>
}

void
${nspPrefix}::${simpleNeuronName}::State_::set(const DictionaryDatum& d)
{
  <#list body.getNonAliasStates() as state>
  ${tc.include("org.nest.nestml.function.ReadFromDictionary", state)}
  </#list>
}

${nspPrefix}::${simpleNeuronName}::Buffers_::Buffers_(${ast.getName()} &n)
: logger_(n)
{}

${nspPrefix}::${simpleNeuronName}::Buffers_::Buffers_(const Buffers_ &, ${ast.getName()} &n)
: logger_(n)
{}

/* ----------------------------------------------------------------
* Default and copy constructor for node
* ---------------------------------------------------------------- */
// TODO inner components
${nspPrefix}::${simpleNeuronName}::${simpleNeuronName}()
: Archiving_Node(),
P_(),
S_(),
B_(*this)
{
  recordablesMap_.create();
}

${nspPrefix}::${simpleNeuronName}::${simpleNeuronName}(const ${simpleNeuronName}& n)
    : Archiving_Node(n),
    P_(n.P_),
    S_(n.S_),
    B_(n.B_, *this)
{}

/* ----------------------------------------------------------------
* Node initialization functions
* ---------------------------------------------------------------- */

void
${nspPrefix}::${simpleNeuronName}::init_state_(const Node& proto)
{ // TODO inner components
  const ${ast.getName()}& pr = downcast<${ast.getName()}>(proto);
  S_ = pr.S_;
}

<#if useGSL>
<#assign ODEs = body.getEquations().get().getODEs>
${tc.include("org.nest.nestml.function.GSLDifferentiationFunction",body)}
</#if>

void
${nspPrefix}::${simpleNeuronName}::init_buffers_()
{
  <#list body.getInputLines() as input>
  ${bufferHelper.printBufferInitialization(input)}
  </#list>
  B_.logger_.reset(); // includes resize
  Archiving_Node::clear_history();
  <#if useGSL>
    if ( B_.s_ == 0 )
    B_.s_ = gsl_odeiv_step_alloc( gsl_odeiv_step_rkf45, ${stateSize} );
    else
    gsl_odeiv_step_reset( B_.s_ );

    if ( B_.c_ == 0 )
    B_.c_ = gsl_odeiv_control_y_new( 1e-3, 0.0 );
    else
    gsl_odeiv_control_init( B_.c_, 1e-3, 0.0, 1.0, 0.0 );

    if ( B_.e_ == 0 )
    B_.e_ = gsl_odeiv_evolve_alloc( ${stateSize} );
    else
    gsl_odeiv_evolve_reset( B_.e_ );

    B_.sys_.function = ${simpleNeuronName}_dynamics;
    B_.sys_.jacobian = NULL;
    B_.sys_.dimension = ${stateSize};
    B_.sys_.params = reinterpret_cast< void* >( this );

  </#if>

}

void
${nspPrefix}::${simpleNeuronName}::calibrate()
{ // TODO init internal variables
  B_.logger_.init();

  ${tc.include("org.nest.nestml.function.Calibrate", body.getNonAliasInternals())}

  <#list body.getInputLines() as inputLine>
    <#if bufferHelper.isVector(inputLine)>
        B_.receptor_types_${inputLine.getName()}.resize(P_.${bufferHelper.vectorParameter(inputLine)});
        for (size_t i=0; i < P_.${bufferHelper.vectorParameter(inputLine)}; i++)
        {
          B_.receptor_types_${inputLine.getName()}[i] = i+1;
        }
    </#if>

  </#list>
}

/* ----------------------------------------------------------------
* Update and spike handling functions
* ---------------------------------------------------------------- */
void
${nspPrefix}::${simpleNeuronName}::update(
        nest::Time const & origin,
        const nest::long_t from, const nest::long_t to)
{
    <#list body.getDynamics() as dynamic>
    ${tc.include("org.nest.nestml.function.DynamicsImplementation", dynamic)}
    </#list>
}

// Do not move this function as inline to h-file. It depends on
// universal_data_logger_impl.h being included here.
void
${nspPrefix}::${simpleNeuronName}::handle(nest::DataLoggingRequest& e)
{
    B_.logger_.handle(e);
}

<#list body.getFunctions() as function>
${functionPrinter.printFunctionDefinition(function, nspPrefix + "::" + simpleNeuronName)}
{
  ${tc.include("org.nest.spl.Block", function.getBlock())}
}
</#list>

<#if isSpikeInput>
void
${nspPrefix}::${simpleNeuronName}::handle(nest::SpikeEvent &e)
{
  assert(e.get_delay() > 0);

  const double_t weight = e.get_weight();
  const double_t multiplicity = e.get_multiplicity();
  ${tc.include("org.nest.nestml.buffer.SpikeBufferFill", body.getInputLines())}
}
</#if>

<#if isCurrentInput>
void
${nspPrefix}::${simpleNeuronName}::handle(nest::CurrentEvent& e)
{
  assert(e.get_delay() > 0);

  const double_t current=e.get_current();
  const double_t weight=e.get_weight();

  // add weighted current; HEP 2002-10-04
  ${tc.include("org.nest.nestml.buffer.CurrentBufferFill", body.getInputLines())}
}
</#if>


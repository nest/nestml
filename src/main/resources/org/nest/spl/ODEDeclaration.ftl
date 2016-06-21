<#--
  @grammar:OdeDeclaration  = "ODE" BLOCK_OPEN (NEWLINE)*
       (Eq (NEWLINE)*)*
       (ODE (NEWLINE)*)+
       BLOCK_CLOSE;
  @param ast ASTOdeDeclration;
  @param tc templatecontroller
  @param stateSize number of the step variables
  @result TODO
-->
<#assign stateSize = body.getStateNonAliasSymbols()?size>
<#assign indexPostfix = "INDEX">

double step_ = nest::Time::get_resolution().get_ms();
double IntegrationStep_ = nest::Time::get_resolution().get_ms();

while ( t < step_ )
{

double stateVector[${stateSize}];
<#assign index = 0>
<#list body.getStateNonAliasSymbols() as stateVariable>
  stateVector[${stateVariable.getName()}_${indexPostfix}] = S_.${stateVariable.getName()};
  <#assign index = index + 1>
</#list>

  const int status = gsl_odeiv_evolve_apply( B_.e_,
  B_.c_,
  B_.s_,
  &B_.sys_,             // system of ODE
  &t,                   // from t
  step_,             // to t <= step
  &IntegrationStep_, // integration step size
  stateVector );               // neuronal state
<#assign index = 0>
<#list body.getStateNonAliasSymbols() as stateVariable>
  S_.${stateVariable.getName()} = stateVector[${stateVariable.getName()}_${indexPostfix}];
  <#assign index = index + 1>
</#list>
}
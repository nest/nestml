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
<#assign stateSize = body.getNonAliasStates()?size>
<#assign indexPostfix = "INDEX">

double step_ = nest::Time::get_resolution().get_ms();
double IntegrationStep_ = nest::Time::get_resolution().get_ms();

while ( t < step_ )
{

double stateVector[${stateSize}];
<#assign index = 0>
<#list ast.getODEs() as ode>
  stateVector[${ode.getLhsVariable()}_${indexPostfix}] = S_.${ode.getLhsVariable()}_;
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
<#list ast.getODEs() as ode>
  S_.${ode.getLhsVariable()}_ = stateVector[${ode.getLhsVariable()}_${indexPostfix}];
  <#assign index = index + 1>
</#list>
}
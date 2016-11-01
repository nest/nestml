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

<#assign index = 0>
<#assign indexPostfix = "INDEX">
<#list body.variablesDefinedByODE() as odeVariable>
  stateVector[${names.name(odeVariable)}_${indexPostfix}] = S_.${names.name(odeVariable)};
  <#assign index = index + 1>
</#list>
while ( t < step_ )
{
  const int status = gsl_odeiv_evolve_apply( B_.e_,
  B_.c_,
  B_.s_,
  &B_.sys_,          // system of ODE
  &t,                // from t
  step_,             // to t <= step
  &IntegrationStep_, // integration step size
  stateVector );     // neuronal state
<#assign index = 0>
  if ( status != GSL_SUCCESS ) {
    throw nest::GSLSolverFailure( get_name(), status );
  }
}
<#list body.variablesDefinedByODE() as odeVariable>
  S_.${names.name(odeVariable)} = stateVector[${names.name(odeVariable)}_${indexPostfix}];
  <#assign index = index + 1>
</#list>
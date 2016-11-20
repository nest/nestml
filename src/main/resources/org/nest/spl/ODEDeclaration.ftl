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
<#assign stateSize = body.getEquations()?size>
<#assign indexPostfix = "INDEX">

double step_ = nest::Time::get_resolution().get_ms();
double IntegrationStep_ = nest::Time::get_resolution().get_ms();
double t = 0;

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
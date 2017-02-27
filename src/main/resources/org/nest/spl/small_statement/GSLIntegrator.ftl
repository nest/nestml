<#--

  @param ast ASTOdeDeclration;
  @param tc templatecontroller
  @param stateSize number of the step variables
  @result TODO
-->
t = 0;

while ( t < B_.__step )
{
  const int status = gsl_odeiv_evolve_apply( B_.__e,
  B_.__c,
  B_.__s,
  &B_.__sys,               // system of ODE
  &t,                     // from t
  B_.__step,              // to t <= step
  &B_.__integration_step, // integration step size
  S_.y );                 // neuronal state

  if ( status != GSL_SUCCESS ) {
    throw nest::GSLSolverFailure( get_name(), status );
  }
}
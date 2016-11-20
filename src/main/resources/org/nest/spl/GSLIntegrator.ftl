<#--

  @param ast ASTOdeDeclration;
  @param tc templatecontroller
  @param stateSize number of the step variables
  @result TODO
-->
t = 0;

while ( t < step_ )
{
  const int status = gsl_odeiv_evolve_apply( B_.e_,
  B_.c_,
  B_.s_,
  &B_.sys_,          // system of ODE
  &t,                // from t
  step_,             // to t <= step
  &IntegrationStep_, // integration step size
  S_.y );            // neuronal state

  if ( status != GSL_SUCCESS ) {
    throw nest::GSLSolverFailure( get_name(), status );
  }
}
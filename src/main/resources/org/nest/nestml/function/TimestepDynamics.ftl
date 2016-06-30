<#--Dynamics implements BodyElement = "dynamics" (MinDelay | TimeStep) "(" Parameter ")"
                                        BLOCK_OPEN! Block BLOCK_CLOSE!;-->

double t;
for ( nest::long_t lag = from ; lag < to ; ++lag ) {
  t = 0;
  ${tc.include("org.nest.spl.Block", ast.getBlock())}

  // voltage logging
  B_.logger_.record_data(origin.get_steps()+lag);
}

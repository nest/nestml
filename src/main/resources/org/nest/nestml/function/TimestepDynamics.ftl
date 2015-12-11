<#--Dynamics implements BodyElement = "dynamics" (MinDelay | TimeStep) "(" Parameter ")"
                                        BLOCK_OPEN! Block BLOCK_CLOSE!;-->
assert(to >= 0 && (nest::delay) from < nest::Scheduler::get_min_delay());
assert(from < to);

${dynamicsHelper.printDynamicsType(ast)} ${dynamicsHelper.printParameterName(ast)};
for ( nest::long_t lag = from ; lag < to ; ++lag ) {
  <#--
  TODO: alternative
  ${dynamicsHelper.printParameterName(ast)} = nest::Time(nest::Time::step( lag )).get_ms() + origin.get_ms();
  -->
  ${dynamicsHelper.printParameterName(ast)} = 0;
  ${tc.include("org.nest.spl.Block", ast.getBlock())}

  // voltage logging
  B_.logger_.record_data(origin.get_steps()+lag);
}

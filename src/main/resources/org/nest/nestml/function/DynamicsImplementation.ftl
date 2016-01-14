<#--
  Generates C++ declaration
  @grammar:   Dynamics implements BodyElement = "dynamics" (MinDelay | TimeStep)
                                    "(" Parameters? ")"
                                      BLOCK_OPEN Block BLOCK_CLOSE;
  @param ast ASTDynamics
  @param tc templatecontroller
  @result TODO
-->
${tc.include("org.nest.nestml.function.TimestepDynamics", ast)}
<#--
  Generates C++ declaration
  @grammar:   Dynamics implements BodyElement = "dynamics" (MinDelay | TimeStep)
                                    "(" Parameters? ")"
                                      BLOCK_OPEN Block BLOCK_CLOSE;
  @param ast ASTDynamics
  @param tc templatecontroller
  @result TODO
-->
<#if ast.getMinDelay().isPresent()>
${tc.include("org.nest.nestml.function.MinDelayDynamics", ast)}
<#elseif ast.getTimeStep().isPresent()>
${tc.include("org.nest.nestml.function.TimestepDynamics", ast)}
</#if>
<#--
  @param ast ASTInputLine
  @param tc templatecontroller
  @result TODO
-->
<#if ast.isCurrent()>
get_${ast.getName()}().add_value(e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin()),
           weight * current );
</#if>

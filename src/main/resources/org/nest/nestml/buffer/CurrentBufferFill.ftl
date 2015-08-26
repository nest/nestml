<#--
  @param ast ASTInputLine
  @param tc templatecontroller
  @result TODO
-->
<#if ast.isCurrent()>
get_${ast.getName()}().add_value(e.get_rel_delivery_steps( network()->get_slice_origin()),
           weight * current );
</#if>

<#--
  @param ast ASTInputLine
  @grammar
    InputLine =
      Name
      ("<" sizeParameter:Name ">")?
      "<-" InputType*
      (["spike"] | ["current"]);

    InputType = (["inhibitory"] | ["excitatory"]);
  @result
-->
<#if ast.isSpike()>
  <#if bufferHelper.isVector(ast)>
    for (size_t i=0; i < P_.${bufferHelper.vectorParameter(ast)}; i++)
    {
      if (B_.receptor_types_${ast.getName()}[i] == e.get_rport()) {
      get_${ast.getName()}()[i].add_value(e.get_rel_delivery_steps(nest::kernel().simulation_manager.get_slice_origin()),
      e.get_weight() * e.get_multiplicity());
      }

    }
  <#else>
    <#if bufferHelper.isExcitatory(ast)>
    if ( weight >= 0.0 ) // excitatory
    {
      get_${ast.getName()}().add_value(e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin()),
                   weight * multiplicity );
    }
    </#if>
    <#if bufferHelper.isInhibitory(ast)>
    if ( weight < 0.0 ) // inhibitory
    {
      get_${ast.getName()}().add_value(e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin()),
                   weight * multiplicity );
    }
    </#if>
  </#if>
</#if>

<#--
  Creates code that describes how to handle incoming spike
  @param ast ASTInputLine
  @grammar:
    InputLine =
      Name
      ("[" sizeParameter:Name "]")?
      "<-" InputType*
      (["spike"] | ["current"]););

    InputType = (["inhibitory"] | ["excitatory"]);
  @result
-->
${signature("buffer")}

<#if buffer.isVector()>
  for (size_t i=0; i < P_.${buffer.getVectorParameter()}; i++)
  {
    if (B_.receptor_types_[i] == e.get_rport()) {
      get_${buffer.getName()}()[i].add_value(e.get_rel_delivery_steps(nest::kernel().simulation_manager.get_slice_origin()),
      e.get_weight() * e.get_multiplicity());
    }

  }
<#else>
  <#if buffer.isExcitatory()>
  if ( weight >= 0.0 ) // excitatory
  {
    get_${buffer.getName()}().add_value(e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin()),
                 weight * multiplicity );
  }
  </#if>
  <#if buffer.isInhibitory()>
  if ( weight < 0.0 ) // inhibitory
  {
    get_${buffer.getName()}().add_value(e.get_rel_delivery_steps( nest::kernel().simulation_manager.get_slice_origin()),
                <#if buffer.isConductanceBased()> // ensure conductance is positive </#if>
                <#if buffer.isConductanceBased()> -1 * </#if> weight * multiplicity );
  }
  </#if>
</#if>

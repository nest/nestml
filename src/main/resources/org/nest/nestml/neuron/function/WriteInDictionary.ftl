<#--
  Generates code that

  @param variable VariableSymbol
-->
${signature("variable")}
<#if !variable.isInternal()>
  def< ${declarations.printVariableType(variable)} >(__d, "${statusNames.name(variable)}", ${names.getter(variable)}());
</#if>
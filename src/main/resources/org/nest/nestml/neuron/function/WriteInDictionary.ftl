<#--
  Generates code that

  @param variable VariableSymbol
-->
${signature("variable")}
<#if !variable.isInternal()>
  def< ${declarations.printVariableType(variable)} >(__d, "${variable.getName()}", ${names.getter(variable)}());
</#if>
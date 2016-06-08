<#--
  Generates code that

  @param variable VariableSymbol
-->
${signature("variable")}
<#if variable.isAlias() && aliasInverter.isRelativeExpression(variable.getDeclaringExpression().get())>
  <#assign baseVariable = variable.getName()>
  <#assign offset = aliasInverter.offsetVariable(variable.getDeclaringExpression().get()).getName()>
  <#assign inverseOperation = aliasInverter.inverseOperation(variable.getDeclaringExpression().get())>
  def< ${declarations.printVariableType(variable)} >(d, "${variable.getName()}", get_${variable.getName()}() ${inverseOperation} get_${offset}());
<#else>
  def< ${declarations.printVariableType(variable)} >(d, "${variable.getName()}", get_${variable.getName()}());
</#if>
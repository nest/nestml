<#--
  Generates code that

  @param variable VariableSymbol
-->
${signature("variable")}
<#if variable.isAlias() && aliasInverter.isRelativeExpression(variable.getDeclaringExpression().get())>
  <#assign baseVariable = variable.getName()>
  <#assign offsetVariable = aliasInverter.offsetVariable(variable.getDeclaringExpression().get())>
  <#assign offset = aliasInverter.offsetVariable(variable.getDeclaringExpression().get()).getName()>
  <#assign inverseOperation = aliasInverter.inverseOperator(variable.getDeclaringExpression().get())>
  def< ${declarations.printVariableType(variable)} >(__d, "${statusNames.name(variable)}", ${names.getter(variable)}() ${inverseOperation} ${names.getter(offsetVariable)}());
<#else>
  def< ${declarations.printVariableType(variable)} >(__d, "${statusNames.name(variable)}", ${names.getter(variable)}());
</#if>
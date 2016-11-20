<#--
  Generates a code snippet that retrieves a data from dictionary and sets it the the model variable.

  @param variable VariableSymbol
  @result C++ Block
-->
${signature("variable")}

<#if variable.isAlias() && variable.hasSetter()>
  // handles an alias with the user defined setter
  ${declarations.printVariableType(variable)} tmp_${statusNames.name(variable)};
  if (updateValue<${declarations.printVariableType(variable)}>(__d, "${statusNames.name(variable)}", tmp_${statusNames.name(variable)})) {
    ${names.setter(variable)}(tmp_${statusNames.name(variable)});
  }

<#elseif variable.isAlias() && aliasInverter.isInvertableExpression(variable.getDeclaringExpression().get()) >
  <#assign baseVariable = aliasInverter.baseVariable(variable.getDeclaringExpression().get())>
  <#assign base = aliasInverter.baseVariable(variable.getDeclaringExpression().get()).getName()>
  <#assign offsetVariable = aliasInverter.offsetVariable(variable.getDeclaringExpression().get())>
  <#assign offset = aliasInverter.offsetVariable(variable.getDeclaringExpression().get()).getName()>
  <#assign inverseOperation = aliasInverter.inverseOperator(variable.getDeclaringExpression().get())>

  if ( updateValue< ${declarations.printVariableType(variable)} >( __d, "${statusNames.name(variable)}", ${variableHelper.printOrigin(baseVariable)}${names.name(baseVariable)} ) ) {
    ${names.setter(baseVariable)}( ${names.getter(baseVariable)}() ${inverseOperation} ${variableHelper.printOrigin(offsetVariable)}${offset});
  }
  else {
    ${names.setter(baseVariable)}( ${names.getter(baseVariable)}() ${inverseOperation} delta_${offset});
  }
<#elseif variable.isAlias() && aliasInverter.isRelativeExpression(variable.getDeclaringExpression().get())>

  <#assign offsetVariable = aliasInverter.offsetVariable(variable.getDeclaringExpression().get())>
  <#assign offset = aliasInverter.offsetVariable(variable.getDeclaringExpression().get()).getName()>
  <#assign inverseOperation = aliasInverter.operator(variable.getDeclaringExpression().get())>
  if ( updateValue< ${declarations.printVariableType(variable)} >( __d, "${statusNames.name(variable)}", ${variableHelper.printOrigin(offsetVariable)}${names.name(variable)} ) ) {
    ${names.setter(variable)}( ${names.getter(variable)}() ${inverseOperation} ${variableHelper.printOrigin(offsetVariable)}${offset});
  }
  else {
    ${names.setter(variable)}( ${names.getter(variable)}() ${inverseOperation} delta_${offset});
  }
<#elseif !variable.isAlias()>
  ${declarations.printVariableType(variable)} tmp_${statusNames.name(variable)};
    if (updateValue<${declarations.printVariableType(variable)}>(__d, "${statusNames.name(variable)}", tmp_${statusNames.name(variable)})) {
    ${names.setter(variable)}( tmp_${statusNames.name(variable)});
  }
<#else>
  // ignores '${statusNames.name(variable)}' ${declarations.printVariableType(variable)}' since it is an alias and setter isn't defined
</#if>

<#--
  Generates a code snippet that retrieves a data from dictionary and sets it the the model variable.

  @param variable VariableSymbol
  @result C++ Block
-->
${signature("variable")}

<#if variable.isAlias() && variable.hasSetter()>
  // handles an alias with the user defined setter
  ${declarations.printVariableType(variable)} tmp_${variable.getName()};
  if (updateValue<${declarations.printVariableType(variable)}>(d, "${variable.getName()}", tmp_${variable.getName()})) {
    set_${variable.getName()}(tmp_${variable.getName()});
  }
<#elseif variable.isAlias() && aliasInverter.isInvertableExpression(variable.getDeclaringExpression().get())>
  <#assign baseVariable = aliasInverter.baseVariable(variable.getDeclaringExpression().get())>
  <#assign base = aliasInverter.baseVariable(variable.getDeclaringExpression().get()).getName()>
  <#assign offset = aliasInverter.offsetVariable(variable.getDeclaringExpression().get()).getName()>
  <#assign inverseOperation = aliasInverter.inverseOperation(variable.getDeclaringExpression().get())>

  <#if baseVariable.isState()>
    if ( updateValue< double >( d, "${variable.getName()}", ${base} ) ) {
      ${base} ${inverseOperation}= p.${offset};
    }
    else {
      ${base} ${inverseOperation}= delta_${offset};
    }
  <#else>
    if ( updateValue< double >( d, "${base}", ${base} ) ) {
      ${base} ${inverseOperation}= ${offset};
    }
    else {
      ${base} ${inverseOperation}= delta_${offset};
    }
  </#if>
<#elseif !variable.isAlias()>
  ${declarations.printVariableType(variable)} tmp_${variable.getName()};
    if (updateValue<${declarations.printVariableType(variable)}>(d, "${variable.getName()}", tmp_${variable.getName()})) {
    ${variable.getName()} = tmp_${variable.getName()};
  }
<#else>
  // ignores '${variable.getName()}' ${declarations.printVariableType(variable)}' since it is an alias and setter isn't defined
</#if>

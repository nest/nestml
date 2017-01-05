<#--
  Generates a code snippet that retrieves a data from dictionary and sets it the the model variable.

  @param variable VariableSymbol
  @result C++ Block
-->
${signature("variable")}
<#if variable.hasSetter() || !variable.isAlias()>
  ${declarations.printVariableType(variable)} tmp_${statusNames.name(variable)} = ${declarations.initialValue(variable)};
  updateValue<${declarations.printVariableType(variable)}>(__d, "${statusNames.name(variable)}", tmp_${statusNames.name(variable)});
<#else>
  // ignores '${statusNames.name(variable)}' ${declarations.printVariableType(variable)}' since it is an function and setter isn't defined
</#if>
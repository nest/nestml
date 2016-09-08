<#--
  Generates C++ declaration

  @param variable VariableSymbol
  @param tc templatecontroller
-->
${signature("variable", "printer")}

<#if variable.getDeclaringExpression().isPresent()>
  <#if variable.isVector()>
    ${variableHelper.printOrigin(variable)}${names.name(variable)}.resize(P_.${variable.getVectorParameter().get()}, ${printer.print(variable.getDeclaringExpression().get())});
  <#elseif variable.isAlias() && !aliasInverter.isRelativeExpression(variable.getDeclaringExpression().get())>
    ${declarations.printVariableType(variable)} ${variableHelper.printOrigin(variable)}${names.name(variable)} = ${printer.print(variable.getDeclaringExpression().get())};
  <#else>
    ${variableHelper.printOrigin(variable)}${names.name(variable)} = ${printer.print(variable.getDeclaringExpression().get())};
  </#if>
<#else>
  <#if variable.isVector()>
    ${variableHelper.printOrigin(variable)}${names.name(variable)}.resize(0);
  <#else>
    ${variableHelper.printOrigin(variable)}${names.name(variable)} = 0;
  </#if>
</#if>

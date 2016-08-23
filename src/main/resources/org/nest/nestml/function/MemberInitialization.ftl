<#--
  Generates C++ declaration

  @param variable VariableSymbol
  @param tc templatecontroller
-->
${signature("variable", "printer")}

<#if variable.getDeclaringExpression().isPresent()>
  <#if variable.isVector()>
    ${names.name(variable)}.resize(${variable.getVectorParameter().get()}, ${printer.print(variable.getDeclaringExpression().get())});
  <#elseif variable.isAlias() && !aliasInverter.isRelativeExpression(variable.getDeclaringExpression().get())>
    ${declarations.printVariableType(variable)} ${names.name(variable)} = ${printer.print(variable.getDeclaringExpression().get())};
  <#else>
    ${names.name(variable)} = ${printer.print(variable.getDeclaringExpression().get())};
  </#if>
<#else>
  <#if variable.isVector()>
    ${names.name(variable)}.resize(0);
  <#else>
    ${names.name(variable)} = 0;
  </#if>
</#if>

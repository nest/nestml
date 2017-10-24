<#--
  In general case creates an

  @param variable VariableSymbol Variable for which the initialization should be done
  @param printer The particular pretty printer which prints expressions. Is used to handel differences where the
                 variable is declared (inside a struct or in another method)
-->
${signature("variable", "printer")}
<#if variable.getDeclaringExpression().isPresent() && !variable.isShape()>
  <#if variable.isVector()>
    ${variableHelper.printOrigin(variable)}${names.name(variable)}.resize(P_.${variable.getVectorParameter().get()}, ${printer.print(variable.getDeclaringExpression().get())}); // as ${variable.getType().prettyPrint()}
  <#else>
    ${variableHelper.printOrigin(variable)}${names.name(variable)} = ${printer.print(variable.getDeclaringExpression().get())}; // as ${variable.getType().prettyPrint()}
  </#if>
<#else>
  <#if variable.isVector()>
    ${variableHelper.printOrigin(variable)}${names.name(variable)}.resize(0); // as ${variable.getType().prettyPrint()}
  <#else>
    ${variableHelper.printOrigin(variable)}${names.name(variable)} = 0; // as ${variable.getType().prettyPrint()}
  </#if>
</#if>

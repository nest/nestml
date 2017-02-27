<#--
 TODO: instead of using 0 a default value provider must be used
-->
${signature("variable")}

<#if variable.getVectorParameter().isPresent()>
${variableHelper.printOrigin(variable)} ${variable.getName()}.resize(P_.${variable.getVectorParameter().get()});
for (long i=0; i < get_${variable.getVectorParameter().get()}(); i++) {
  ${variableHelper.printOrigin(variable)} ${variable.getName()}[i] =
    <#if variable.getDeclaringExpression().isPresent()>
    ${expressionsPrinter.print(variable.getDeclaringExpression().get())}
    <#else>
    0
    </#if>
  ;
}
<#else>
${variableHelper.printOrigin(variable)} ${variable.getName()} =
  <#if variable.getDeclaringExpression().isPresent()>
    ${expressionsPrinter.print(variable.getDeclaringExpression().get())}
  <#else>
  0
  </#if>;
</#if>

<#--
  Generates C++ declaration
  @grammar:  Declaration =
                vars:Name ("," vars:Name)*
                Datatype
                ("[" sizeParameter:Name "]")?
                ( "=" Expr )? ;

  @param variable VariableSymbol
  @param tc templatecontroller
-->
${signature("variable")}
<#if variable.getDeclaringExpression().isPresent()>
  <#if !variable.isVector()>
    ${variable.getName()} = ${expressionsPrinter.print(variable.getDeclaringExpression().get())};
  <#else>
    ${variable.getName()}.resize(${variable.getVectorParameter().get()}, ${expressionsPrinter.print(variable.getDeclaringExpression().get())});
  </#if>
<#else>
  <#if !variable.isVector()>
    ${variable.getName()} = 0;
  <#else>
    ${variable.getName()}.resize(${variable.getVectorParameter().get()}, 0);
  </#if>
</#if>

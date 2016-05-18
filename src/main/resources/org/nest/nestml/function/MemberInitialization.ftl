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
    ${variable.getName()}_ = ${expressionsPrinter.print(variable.getDeclaringExpression().get())};
  </#if>

</#if>

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
${signature("variable", "printer")}

<#if variable.getDeclaringExpression().isPresent()>
  <#if variable.isVector()>
    ${variable.getName()}.resize(${variable.getVectorParameter().get()}, ${printer.print(variable.getDeclaringExpression().get())});
  <#elseif variable.isAlias()>
    ${declarations.printVariableType(variable)} ${variable.getName()} = ${printer.print(variable.getDeclaringExpression().get())};
  <#else>
    ${variable.getName()} = ${printer.print(variable.getDeclaringExpression().get())};
  </#if>
<#else>
  <#if variable.isVector()>
    ${variable.getName()}.resize(0);
  <#else>
    ${variable.getName()} = 0;
  </#if>
</#if>

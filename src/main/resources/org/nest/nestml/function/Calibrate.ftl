<#--

  @grammar: AliasDecl = ([hide:"-"])? ([alias:"alias"])?
                        Declaration ("[" invariants:Expr (";" invariants:Expr)* "]")?;
                        Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expr )? ;
  @param variable VariableSymbol
  @result Generates C++ declaration
-->
${signature("variable")}

<#if variable.getVectorParameter().isPresent()>
${variableHelper.printOrigin(variable)} ${variable.getName()}.resize(P_.${variable.getVectorParameter().get()});
for (size_t i=0; i < get_${variable.getVectorParameter().get()}(); i++) {
  ${variableHelper.printOrigin(variable)} ${variable.getName()}[i] =
    <#if variable.getDeclaringExpression().isPresent()>
    ${tc.include("org.nest.spl.expr.Expr", variable.getDeclaringExpression().get())}
    <#else>
    0
    </#if>
  ;
}
<#else>
${variableHelper.printOrigin(variable)} ${variable.getName()} =
  <#if variable.getDeclaringExpression().isPresent()>
    ${tc.include("org.nest.spl.expr.Expr", variable.getDeclaringExpression().get())}
  <#else>
  0
  </#if>;
</#if>

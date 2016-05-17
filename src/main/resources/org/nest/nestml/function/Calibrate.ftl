<#--
  Generates C++ declaration
  @grammar: AliasDecl = ([hide:"-"])? ([alias:"alias"])?
                        Declaration ("[" invariants:Expr (";" invariants:Expr)* "]")?;
                        Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expr )? ;
  @param ast ASTAliasDecl
  @param tc templatecontroller
  @result TODO
-->
${signature("variable")}

<#if variable.getArraySizeParameter().isPresent()>
resize_${variable.getName()}(${variable.getArraySizeParameter().get()}());
for (size_t i=0; i < get_${variable.getArraySizeParameter().get()}(); i++) {
  get_${variable.getName()}()[i] =
    <#if variable.getDeclaringExpression().isPresent()>
    ${tc.include("org.nest.spl.expr.Expr", variable.getDeclaringExpression().get())}
    <#else>
    0
    </#if>
  ;
}
<#else>
set_${variable.getName()}(
  <#if variable.getDeclaringExpression().isPresent()>
    ${tc.include("org.nest.spl.expr.Expr", variable.getDeclaringExpression().get())}
  <#else>
  0
  </#if> );
</#if>

<#--
  Generates C++ declaration
  @grammar: AliasDecl = ([hide:"-"])? ([alias:"alias"])?
                        Declaration ("[" invariants:Expr (";" invariants:Expr)* "]")?;
                        Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expr )? ;
  @param ast ASTAliasDecl
  @param tc templatecontroller
  @result TODO
-->
<#list declarations.getVariables(ast) as var>
<#if declarations.isVectorType(ast)>
for (size_t i=0; i < get_num_of_receptors(); i++) {
  get_${var.getName()}()[i] =
    <#if ast.getDeclaration().getExpr().isPresent()>
    ${tc.include("org.nest.spl.expr.Expr", ast.getDeclaration().getExpr().get())}
    <#else>
    0
    </#if>
  ;
}
<#else>
set_${var.getName()}(
  <#if ast.getDeclaration().getExpr().isPresent()>
  ${tc.include("org.nest.spl.expr.Expr", ast.getDeclaration().getExpr().get())}
  <#else>
  0
  </#if> );
</#if>



</#list>

<#--
  Generates C++ declaration
  @grammar:
  Declaration =
    vars:Name ("," vars:Name)*
    (type:QualifiedName | primitiveType:PrimitiveType)
    ("<" sizeParameter:Name ">")?
    ( "=" Expr )? ;
  @param ast ASTDeclaration
-->
<#assign declarationType = declarations.getDeclarationType(ast)>

<#list declarations.getVariables(ast) as variableName>
  ${declarationType} ${variableName}
  <#if ast.getExpr().isPresent()>
    = ${tc.include("org.nest.spl.expr.Expr", ast.getExpr().get())}
  </#if>;
</#list>

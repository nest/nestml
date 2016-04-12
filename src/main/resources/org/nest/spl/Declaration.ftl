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

<#list declarations.getVariables(ast) as variable>
  ${declarations.printVariableType(variable)} ${variable.getName()}
  <#if ast.getExpr().isPresent()>
    = ${tc.include("org.nest.spl.expr.Expr", ast.getExpr().get())}
  </#if>;
</#list>

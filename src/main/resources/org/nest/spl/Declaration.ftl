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

  ${declarations.printVariableType(variable)} ${variable.getName()};
  <#-- The declaration is decoupled into the declaration and assignment because otherwise the vectorized version would not work properly-->

  <#if ast.getExpr().isPresent()>
    <#if declarations.isVector(ast)>
      for (size_t i=0; i < get_${declarations.printSizeParameter(ast)}(); i++) {
        ${variable.getName()}[i] = ${tc.include("org.nest.spl.expr.Expr", ast.getExpr().get())};
      }
    <#else>
      ${variable.getName()} = ${tc.include("org.nest.spl.expr.Expr", ast.getExpr().get())};
    </#if>
  </#if>
</#list>

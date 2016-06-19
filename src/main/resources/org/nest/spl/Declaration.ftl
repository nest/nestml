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

  <#if declarations.isVector(ast)>
    ${declarations.printVariableType(variable)} ${variable.getName()}(P_.${declarations.printSizeParameter(ast)});
    <#if ast.getExpr().isPresent()>
      for (size_t i=0; i < get_${declarations.printSizeParameter(ast)}(); i++) {
        ${variable.getName()}[i] = ${tc.include("org.nest.spl.expr.Expr", ast.getExpr().get())};
      }
    </#if>
  <#else>
    <#if ast.getExpr().isPresent()>
      ${declarations.printVariableType(variable)} ${variable.getName()} = ${tc.include("org.nest.spl.expr.Expr", ast.getExpr().get())};
    <#else>
      ${declarations.printVariableType(variable)} ${variable.getName()};
    </#if>
  </#if>
</#list>

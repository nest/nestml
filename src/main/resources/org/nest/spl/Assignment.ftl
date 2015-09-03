<#--
  Generates C++ declaration
  @grammar: Assignment = variableName:QualifiedName "=" Expr;
  @param ast ASTAssignment
  @param tc templatecontroller
  @result TODO
-->
<#if assignmentHelper.isLocal(ast)>
${assignmentHelper.printVariableName(ast)} = ${tc.include("org.nest.spl.expr.Expr", ast.getExpr())};
<#else>

  <#if assignmentHelper.isVector(ast) || declarations.isVectorLHS(ast)>
  for (size_t i=0; i < declarations.printSizeParameter(ast); i++) {
    <#if declarations.isVectorLHS(ast)>
      ${assignmentHelper.printGetterName(ast)}()[i] = ${tc.include("org.nest.spl.expr.Expr", ast.getExpr())};
    <#else>
      ${assignmentHelper.printSetterName(ast)}(${tc.include("org.nest.spl.expr.Expr", ast.getExpr())});
    </#if>

  }
  <#else>
    ${assignmentHelper.printSetterName(ast)}(${tc.include("org.nest.spl.expr.Expr", ast.getExpr())});
  </#if>

</#if>

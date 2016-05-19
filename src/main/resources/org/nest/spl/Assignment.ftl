<#--
  Generates C++ declaration
  @grammar: Assignment = variableName:QualifiedName "=" Expr;
  @param ast ASTAssignment
  @param tc templatecontroller
  @result TODO
-->

<#if assignments.isVector(ast) || assignments.isVectorLHS(ast)>
for (size_t i=0; i < get_${assignments.printSizeParameter(ast)}(); i++) {
  <#if assignments.isVectorLHS(ast)>
    ${assignments.printOrigin(ast)}.${assignments.printLHS(ast)}_[i]
  <#else>
    ${assignments.printOrigin(ast)}.${assignments.printLHS(ast)}_
  </#if>
  ${assignments.printAssignmentsOperation(ast)} ${tc.include("org.nest.spl.expr.Expr", ast.getExpr())};
}
<#else>
  ${assignments.printOrigin(ast)}.${assignments.printLHS(ast)}_ ${assignments.printAssignmentsOperation(ast)} ${tc.include("org.nest.spl.expr.Expr", ast.getExpr())};
</#if>

<#--
  Generates C++ declaration
  @grammar: Assignment = variableName:QualifiedName "=" Expr;
  @param ast ASTAssignment
  @param tc templatecontroller
  @result TODO
-->
<#assign lhsVariable = assignments.lhsVariable(ast)>
<#if assignments.isVectorizedAssignment(ast)>
for (long i=0; i < P_.${assignments.printSizeParameter(ast)}; i++) {
  <#if lhsVariable.isVector()>
    ${variableHelper.printOrigin(lhsVariable)} ${names.name(lhsVariable)}[i]
  <#else>
    ${variableHelper.printOrigin(lhsVariable)} ${names.name(lhsVariable)}
  </#if>
  ${assignments.printAssignmentsOperation(ast)}
  ${expressionsPrinter.print(ast.getExpr())};
}
<#else>
  ${variableHelper.printOrigin(lhsVariable)}${names.name(lhsVariable)}
  ${assignments.printAssignmentsOperation(ast)}
  ${expressionsPrinter.print(ast.getExpr())};
</#if>

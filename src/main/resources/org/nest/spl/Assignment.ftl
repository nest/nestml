<#--
  Generates C++ declaration
  @grammar: Assignment = variableName:QualifiedName "=" Expr;
  @param ast ASTAssignment
  @param tc templatecontroller
  @result TODO
-->
<#if assignments.isLocal(ast)>

${assignments.printVariableName(ast)} ${assignments.printAssignmentsOperation(ast)} ${tc.include("org.nest.spl.expr.Expr", ast.getExpr())};
<#if assignments.isVector(ast) || declarations.isVectorLHS(ast)>
  for (size_t i=0; i < get_${declarations.printSizeParameter(ast)}(); i++) {
    <#if declarations.isVectorLHS(ast)>
      ${assignments.printVariableName(ast)}[i] = ${tc.include("org.nest.spl.expr.Expr", ast.getExpr())};
    <#else>
      <#if assignments.isCompoundAssignment(ast)>
        ${assignments.printSetterName(ast)}(
        ${assignments.printGetterName(ast)}()
        ${assignments.printCompoundOperation(ast)}
        ${tc.include("org.nest.spl.expr.Expr", ast.getExpr())});
      <#else>
        ${assignments.printSetterName(ast)}(${tc.include("org.nest.spl.expr.Expr", ast.getExpr())});
      </#if>
    </#if>

  }
  <#else>
    <#if assignments.isCompoundAssignment(ast)>
      ${assignments.printSetterName(ast)}(
      ${assignments.printGetterName(ast)}()
      ${assignments.printCompoundOperation(ast)}
      ${tc.include("org.nest.spl.expr.Expr", ast.getExpr())});
    <#else>
      ${assignments.printSetterName(ast)}(${tc.include("org.nest.spl.expr.Expr", ast.getExpr())});
    </#if>

  </#if>
<#else>
  <#if assignments.isVector(ast) || declarations.isVectorLHS(ast)>
  for (size_t i=0; i < get_${declarations.printSizeParameter(ast)}(); i++) {
    <#if declarations.isVectorLHS(ast)>
      ${assignments.printGetterName(ast)}()[i] = ${tc.include("org.nest.spl.expr.Expr", ast.getExpr())};
    <#else>
      <#if assignments.isCompoundAssignment(ast)>
        ${assignments.printSetterName(ast)}(
        ${assignments.printGetterName(ast)}()
        ${assignments.printCompoundOperation(ast)}
        ${tc.include("org.nest.spl.expr.Expr", ast.getExpr())});
      <#else>
        ${assignments.printSetterName(ast)}(${tc.include("org.nest.spl.expr.Expr", ast.getExpr())});
      </#if>
    </#if>

  }
  <#else>
    <#if assignments.isCompoundAssignment(ast)>
      ${assignments.printSetterName(ast)}(
      ${assignments.printGetterName(ast)}()
      ${assignments.printCompoundOperation(ast)}
      ${tc.include("org.nest.spl.expr.Expr", ast.getExpr())});
    <#else>
      ${assignments.printSetterName(ast)}(${tc.include("org.nest.spl.expr.Expr", ast.getExpr())});
    </#if>

  </#if>

</#if>

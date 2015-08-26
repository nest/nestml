<#--
  @grammar:
  @param ast ASTStmt ReturnStmt = "return" Expr?;
  @param tc templatecontroller
  @result TODO
-->
<#if ast.getExpr().isPresent()>
return ${tc.include("org.nest.spl.expr.Expr", ast.getExpr().get())};
<#elseif ast.getCompound_Stmt().isPresent()>
return ;
</#if>
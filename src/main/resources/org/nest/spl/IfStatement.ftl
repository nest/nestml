<#--
  Generates C++ declaration
  @grammar:   IF_Stmt = IF_Clause
                        ELIF_Clause*
                        (ELSE_Clause)?
                        BLOCK_CLOSE;
                        IF_Clause = "if" Expr BLOCK_OPEN Block;
                        ELIF_Clause = "elif" Expr BLOCK_OPEN Block;

  @param ast ASTIF_Stmt
  @param tc templatecontroller
  @result TODO
-->

if (${tc.include("org.nest.spl.expr.Expr", ast.getIF_Clause().getExpr())}) {
${tc.include("org.nest.spl.Block", ast.getIF_Clause().getBlock())}
<#list ast.getELIF_Clauses() as elif>
} else if(${tc.include("org.nest.spl.expr.Expr", elif.getExpr())}) {
${tc.include("org.nest.spl.Block", elif.getBlock())}
</#list>
<#if ast.getELSE_Clause().isPresent()>
}
else {
${tc.include("org.nest.spl.Block", ast.getELSE_Clause().get().getBlock())}
</#if>
} /* if end */


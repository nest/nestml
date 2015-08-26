<#--
  Generates C++ declaration
  @grammar: WHILE_Stmt = "while" Expr BLOCK_OPEN Block BLOCK_CLOSE;
  @param ast ASTWHILE_Stmt
  @param tc templatecontroller
  @result TODO
-->
while(${tc.include("org.nest.spl.expr.Expr", ast.getExpr())}) {
${tc.include("org.nest.spl.Block", ast.getBlock())}
} /* while end */
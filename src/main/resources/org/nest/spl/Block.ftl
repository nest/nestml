<#--
  Handles a complex block statement
  @grammar: Block = ( Stmt | SL_COMMENT | NEWLINE )*;
  @param ast ASTBlock
  @param tc templatecontroller
  @result TODO
-->
<#list ast.getStmts() as statement>
  ${tc.include("org.nest.spl.Statement", statement)}
</#list>
<#--
  Handles a complex block statement
  @grammar: Simple_Stmt = Small_Stmt (";" Small_Stmt)* (";")?;
  @param ast ASTSimple_Stmt
  @param tc templatecontroller
  @result TODO
-->
<#list ast.getSmall_Stmts() as smallStatement>
${tc.include("org.nest.spl.SmallStatement", smallStatement)}
</#list>
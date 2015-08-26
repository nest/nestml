<#--
  @grammar: Stmt = Simple_Stmt ((SL_COMMENT | NEWLINE)* | EOF) | Compound_Stmt;
  @param ast ASTStmt
  @param tc templatecontroller
  @result TODO
-->
<#if ast.getSimple_Stmt().isPresent()>
${tc.include("org.nest.spl.SimpleStmt", ast.getSimple_Stmt().get())}
<#elseif ast.getCompound_Stmt().isPresent()>
${tc.include("org.nest.spl.CompoundStatement", ast.getCompound_Stmt().get())}
</#if>
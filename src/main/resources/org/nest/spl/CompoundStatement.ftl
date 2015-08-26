<#--
  @grammar: Compound_Stmt = IF_Stmt
                | FOR_Stmt
                | WHILE_Stmt;

  @param ast ASTCompound_Stmt
  @param tc templatecontroller
  @result TODO
-->
<#if ast.getIF_Stmt().isPresent()>
${tc.include("org.nest.spl.IfStatement", ast.getIF_Stmt().get())}
<#elseif ast.getFOR_Stmt().isPresent()>
${tc.include("org.nest.spl.ForStatement", ast.getFOR_Stmt().get())}
<#elseif ast.getWHILE_Stmt().isPresent()>
${tc.include("org.nest.spl.WhileStatement", ast.getWHILE_Stmt().get())}
</#if>
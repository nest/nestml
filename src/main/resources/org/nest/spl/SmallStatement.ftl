<#--
  @grammar: Small_Stmt = Assignment
             | FunctionCall
             | Declaration
             | ReturnStmt;
  @param ast ASTSmall_Stmt
  @param tc templatecontroller
  @result TODO
-->
<#if ast.getAssignment().isPresent()>
  ${tc.include("org.nest.spl.small_statement.Assignment", ast.getAssignment().get())}
<#elseif ast.getFunctionCall().isPresent()>
  ${tc.include("org.nest.spl.small_statement.FunctionCall", ast.getFunctionCall().get())}
<#elseif ast.getDeclaration().isPresent()>
  ${tc.include("org.nest.spl.small_statement.Declaration", ast.getDeclaration().get())}
<#elseif ast.getReturnStmt().isPresent()>
  ${tc.include("org.nest.spl.small_statement.ReturnStatement", ast.getReturnStmt().get())}
</#if>
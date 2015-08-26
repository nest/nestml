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
${tc.include("org.nest.spl.Assignment", ast.getAssignment().get())}
<#elseif ast.getFunctionCall().isPresent()>
${tc.include("org.nest.spl.FunctionCall", ast.getFunctionCall().get())}
<#elseif ast.getDeclaration().isPresent()>
${tc.include("org.nest.spl.Declaration", ast.getDeclaration().get())}
<#elseif ast.getReturnStmt().isPresent()>
${tc.include("org.nest.spl.ReturnStatement", ast.getReturnStmt().get())}
</#if>
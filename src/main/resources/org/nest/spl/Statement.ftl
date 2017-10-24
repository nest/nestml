<#if astUtils.printComments(ast)?length != 0>
// ${astUtils.printComments(ast)}
</#if>
<#if ast.getSmall_Stmt().isPresent()>
  ${tc.include("org.nest.spl.SmallStatement", ast.getSmall_Stmt().get())}
<#elseif ast.getCompound_Stmt().isPresent()>
  ${tc.include("org.nest.spl.CompoundStatement", ast.getCompound_Stmt().get())}
</#if>
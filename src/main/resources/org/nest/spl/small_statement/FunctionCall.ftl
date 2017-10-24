<#--
  Generates C++ declaration
  @grammar:   FunctionCall = QualifiedName "(" ArgList ")";
              ArgList = (args:Expr ("," args:Expr)*)?;
  @param ast ASTFunctionCall
  @param tc templatecontroller
  @result TODO
-->
<#if functions.isIntegrate(ast)>
${tc.include("org.nest.spl.small_statement.GSLIntegrator", body)}
<#else>
${expressionsPrinter.printFunctionCall(ast)};
</#if>

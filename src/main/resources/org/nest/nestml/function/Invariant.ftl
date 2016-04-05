<#--
  Invariant checker as C++ code
  @grammar: ASTExpression
  @param ast ASTAliasDecl
  @param tc templatecontroller
-->
if ( !(${expressionsPrinter.print(ast)}) ) {
  throw nest::BadProperty("The invariant '${expressionsPrinterForGSL.print(ast)}' is violated!");
}
<#--
  Generates C++ statements that implement for loop
  @param ast ASTFOR_Stmt
  @param tc templatecontroller
  @param expressionsPrinter ExpressionsPrinter that prints expressions
  @result For-Loop
-->
for( ${ast.getVar()} =  ${expressionsPrinter.print(ast.getFrom())} ;
     ${ast.getVar()} ${forDeclarationHelper.printComparisonOperator(ast)} ${expressionsPrinter.print(ast.getTo())};
     ${ast.getVar()} += ${forDeclarationHelper.printStep(ast)} )
{
  ${tc.include("org.nest.spl.Block", ast.getBlock())}
} /* for end */


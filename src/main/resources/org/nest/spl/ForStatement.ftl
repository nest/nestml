<#--
  Generates C++ declaration
  @grammar:   FOR_Stmt = "for" var:Name "in" from:Expr "..." to:Expr ("step" step:SignedNumericLiteral)? BLOCK_OPEN Block BLOCK_CLOSE;
  @param ast ASTFOR_Stmt
  @param tc templatecontroller
  @result TODO
-->
for( ${ast.getVar()} =  ${expressionsPrinter.print(ast.getFrom())} ;
     ${ast.getVar()} ${forDeclarationHelper.printComparisonOperator(ast)} ${expressionsPrinter.print(ast.getTo())};
     ${ast.getVar()} += ${forDeclarationHelper.printStep(ast)} )
{
     ${tc.include("org.nest.spl.Block", ast.getBlock())}
} /* for end */


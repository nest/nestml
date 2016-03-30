<#--
  Generates C++ declaration
  @grammar: AliasDecl =
                ([log:"log"] | [suppress:"suppress"])? (["alias"])?
                Declaration
                ("|" invariants:Expr (";" invariants:Expr)* )?;
  @param ast ASTAliasDecl
  @param tc templatecontroller
  @result TODO
-->
if ( !(${tc.include("org.nest.spl.expr.Expr", ast)}) ) {
  throw nest::BadProperty("Message");
}
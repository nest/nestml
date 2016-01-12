<#--
  Generates C++ declaration
  @grammar: AliasDecl = ([hide:"-"])? ([alias:"alias"])?
                        Declaration ("[" invariants:Expr (";" invariants:Expr)* "]")?;
                        Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expr )? ;
  @param ast ASTAliasDecl
  @param tc templatecontroller
  @result TODO
-->
<#list declarations.getVariables(ast) as var>

<#if !var.isAlias() && !var.isInState()>
def<${declarations.getType(ast)}>(d, "${var.getName()}", get_${var.getName()}());
<#else>
// do not export ${var.getName()}
</#if>

</#list>

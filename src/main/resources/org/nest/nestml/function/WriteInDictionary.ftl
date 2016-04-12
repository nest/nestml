<#--
  Generates C++ declaration
  @grammar: AliasDecl = ([hide:"-"])? ([alias:"alias"])?
                        Declaration ("[" invariants:Expr (";" invariants:Expr)* "]")?;
                        Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expr )? ;
  @param ast ASTAliasDecl
  @param tc templatecontroller
  @result TODO
-->
${signature("variable")}

<#if !variable.isAlias() && !variable.isInState()>
def<${declarations.printVariableType(variable)}>(d, "${variable.getName()}", get_${variable.getName()}());
<#else>
// do not export ${variable.getName()}
</#if>

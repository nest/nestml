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
<#if variable.isAlias()>
inline ${declarations.printVariableType(variable)} get_${variable.getName()}() const {
  return ${expressionsPrinter.print(variable.getDeclaringExpression().get())};
}
<#else>
inline ${declarations.printVariableType(variable)} get_${variable.getName()}() const {
  return ${variable.getName()};
}
inline void set_${variable.getName()}(const ${declarations.printVariableType(variable)} ${variable.getName()}) {
  this->${variable.getName()} = ${variable.getName()};
}
</#if>


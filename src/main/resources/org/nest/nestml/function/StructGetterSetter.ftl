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
inline ${declarations.printVariableType(variable)} get_${variable.getName()}() const { return ${variable.getName()}_ ; }
inline void set_${variable.getName()}(const ${declarations.printVariableType(variable)} v) { ${variable.getName()}_ = v ; }

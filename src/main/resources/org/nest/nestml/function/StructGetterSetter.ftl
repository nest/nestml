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
inline ${declarations.getType(ast)} get_${var.getName()}() const { return ${var.getName()}_ ; }
inline void set_${var.getName()}(const ${declarations.getType(ast)} v) { ${var.getName()}_ = v ; }
</#list>

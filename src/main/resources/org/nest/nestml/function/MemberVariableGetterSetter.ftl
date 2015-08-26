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
    <#if !var.isAlias()>
    inline ${declarations.getType(ast)} get_${var.getName()}() const {
      return ${declarations.getAliasOrigin(ast)}.get_${var.getName()}() ;
    }
    <#else>
    inline ${declarations.getType(ast)} get_${var.getName()}() const {
      return ${tc.include("org.nest.spl.expr.Expr", ast.getDeclaration().getExpr().get())};
    }
    </#if>
    <#if !var.isAlias()>
    inline void set_${var.getName()}(const ${declarations.getType(ast)} v) {
      ${declarations.getAliasOrigin(ast)}.set_${var.getName()}( v ) ;
    }
    </#if>

</#list>

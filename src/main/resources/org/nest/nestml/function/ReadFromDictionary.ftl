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

<#if var.isAlias() && !var.isInState()>
  // handles an alias
  ${declarations.getType(ast)} tmp_${var.getName()};
    if (updateValue<${declarations.getType(ast)}>(d, "${var.getName()}", tmp_${var.getName()})) {
    set_${var.getName()}(tmp_${var.getName()});
  }
  else {
    set_${var.getName()}(old_${var.getName()});
  }
<#else>
  ${declarations.getType(ast)} tmp_${var.getName()};
    if (updateValue<${declarations.getType(ast)}>(d, "${var.getName()}", tmp_${var.getName()})) {
    set_${var.getName()}(tmp_${var.getName()});
  }

</#if>

</#list>

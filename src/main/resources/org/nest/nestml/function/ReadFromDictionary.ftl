<#--
  Generates C++ declaration
  @grammar: AliasDecl = ([hide:"-"])? ([alias:"alias"])?
                        Declaration ("[" invariants:Expr (";" invariants:Expr)* "]")?;
                        Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expr )? ;
  @param ast ASTAliasDecl
  @param tc templatecontroller
  @result C++ Statements
-->
${signature("var")}

<#if var.hasSetter()>
  <#if var.isAlias() && !var.isInState()>
    // handles an alias
    ${declarations.printVariableType(var)} tmp_${var.getName()};
      if (updateValue<${declarations.printVariableType(var)}>(d, "${var.getName()}", tmp_${var.getName()})) {
      set_${var.getName()}(tmp_${var.getName()});
    }
    else {
      set_${var.getName()}(old_${var.getName()});
    }
  <#else>
    ${declarations.printVariableType(var)} tmp_${var.getName()};
      if (updateValue<${declarations.printVariableType(var)}>(d, "${var.getName()}", tmp_${var.getName()})) {
      set_${var.getName()}(tmp_${var.getName()});
    }

  </#if>
<#else>
  // ignores '${var.getName()}' ${declarations.printVariableType(var)}' since no setter is defined
</#if>

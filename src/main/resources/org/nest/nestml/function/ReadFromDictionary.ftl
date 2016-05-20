<#--
  Generates a code snippet that retrieves a data from dictionary and sets it the the provided

  @param var VariableSymbol
  @param tc templatecontroller
  @result C++ Block
-->
${signature("var")}

<#if var.isAlias() && var.hasSetter()>
  // handles an alias
  ${declarations.printVariableType(var)} tmp_${var.getName()};
    if (updateValue<${declarations.printVariableType(var)}>(d, "${var.getName()}", tmp_${var.getName()})) {
    set_${var.getName()}(tmp_${var.getName()});
  }
  else {
    set_${var.getName()}(old_${var.getName()});
  }
<#elseif !var.isAlias()>
  ${declarations.printVariableType(var)} tmp_${var.getName()};
    if (updateValue<${declarations.printVariableType(var)}>(d, "${var.getName()}", tmp_${var.getName()})) {
    ${var.getName()} = tmp_${var.getName()};
  }
<#else>
  // ignores '${var.getName()}' ${declarations.printVariableType(var)}' since it is an alias and setter isn't defined
</#if>

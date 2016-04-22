<#--
  Generates C++ getter for the provided variable

  @param var VariableSymbol
  @result C++ function
-->
${signature("var")}

<#if !var.isAlias()>
inline ${declarations.printVariableType(var)} get_${var.getName()}() const {
  return ${declarations.getAliasOrigin(var)}.get_${var.getName()}() ;
}
<#else>
inline ${declarations.printVariableType(var)} get_${var.getName()}() const {
  return ${tc.include("org.nest.spl.expr.Expr", var.getDeclaringExpression().get())};
}
</#if>
<#if !var.isAlias()>
inline void set_${var.getName()}(const ${declarations.printVariableType(var)} v) {
  ${declarations.getAliasOrigin(var)}.set_${var.getName()}( v ) ;
}
</#if>

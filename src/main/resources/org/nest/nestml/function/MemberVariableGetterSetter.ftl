<#--
  Generates C++ getter for the provided variable

  @param var VariableSymbol
  @result C++ function
-->
${signature("var")}

<#if !var.isAlias()>
inline ${declarations.printVariableType(var)} get_${var.getName()}() const {
  return ${variableHelper.printOrigin(var)} ${var.getName()} ;
}

inline void set_${var.getName()}(const ${declarations.printVariableType(var)} v) {
  ${variableHelper.printOrigin(var)} ${var.getName()} = v ;
}
<#else>
inline ${declarations.printVariableType(var)} get_${var.getName()}() const {
  return ${tc.include("org.nest.spl.expr.Expr", var.getDeclaringExpression().get())};
}
</#if>

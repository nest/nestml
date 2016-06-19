<#--
  Generates C++ getter for the provided variable

  @param var VariableSymbol
  @result C++ function
-->
${signature("var")}

<#if var.isAlias()>
  <#if aliasInverter.isRelativeExpression(var.getDeclaringExpression().get())>
    inline ${declarations.printVariableType(var)} get_${var.getName()}() const {
      return ${variableHelper.printOrigin(var)} ${var.getName()};
    }
  <#else>
    inline ${declarations.printVariableType(var)} get_${var.getName()}() const {
      return ${tc.include("org.nest.spl.expr.Expr", var.getDeclaringExpression().get())};
    }
  </#if>
<#else>
  inline ${declarations.printVariableType(var)} get_${var.getName()}() const {
    return ${variableHelper.printOrigin(var)} ${var.getName()};
  }

  inline void set_${var.getName()}(const ${declarations.printVariableType(var)} v) {
    ${variableHelper.printOrigin(var)} ${var.getName()} = v;
  }
</#if>

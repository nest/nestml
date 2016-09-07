<#--
  Generates the getter function for the variable.

  @param var VariableSymbol that captures the varibale from the model
  @result C++ function
-->
${signature("var")}

<#if var.isAlias()>
  <#if aliasInverter.isRelativeExpression(var.getDeclaringExpression().get()) || var.isInEquation()>
    inline ${declarations.printVariableType(var)} ${names.getter(var)}() const {
      return ${variableHelper.printOrigin(var)} ${names.name(var)};
    }
  <#else>
    inline ${declarations.printVariableType(var)} ${names.getter(var)}() const {
      <#assign simpleExpression = odeTransformer.replaceSumCalls(var.getDeclaringExpression().get())>
      return ${tc.include("org.nest.spl.expr.Expr", simpleExpression)};
    }
  </#if>
<#else>
  inline ${declarations.printVariableType(var)} ${names.getter(var)}() const {
    return ${variableHelper.printOrigin(var)} ${names.name(var)};
  }

  inline void ${names.setter(var)}(const ${declarations.printVariableType(var)} v) {
    ${variableHelper.printOrigin(var)} ${names.name(var)} = v;
  }
</#if>

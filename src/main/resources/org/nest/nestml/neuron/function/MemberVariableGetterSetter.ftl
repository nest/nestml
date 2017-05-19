<#--
  Generates the getter function for the variable.

  @param variable VariableSymbol that captures the variable from the model
  @result C++ function
-->
${signature("variable")}

<#if variable.isFunction() && !variable.containsSumCall()>
  inline ${declarations.printVariableType(variable)} ${names.getter(variable)}() const {
    <#assign simpleExpression = odeTransformer.replaceSumCalls(variable.getDeclaringExpression().get())>
    return ${expressionsPrinter.print(simpleExpression)};
  }
<#else>
  inline ${declarations.printVariableType(variable)} ${names.getter(variable)}() const {
    return ${variableHelper.printOrigin(variable)} ${names.name(variable)};
  }

  inline void ${names.setter(variable)}(const ${declarations.printVariableType(variable)} __v) {
    ${variableHelper.printOrigin(variable)} ${names.name(variable)} = __v;
  }
</#if>
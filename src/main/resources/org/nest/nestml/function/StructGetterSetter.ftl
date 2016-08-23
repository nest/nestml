<#--
  Generates the getter function for the variable that is defined directly in one of the structs:
  Variables_, Buffers_, Internals_, or State_.

  @param var VariableSymbol that captures the varibale from the model
  @result C++ function
-->
${signature("variable")}
<#if variable.isAlias()>
inline ${declarations.printVariableType(variable)} ${names.getter(variable)}() const {
  return ${expressionsPrinter.print(variable.getDeclaringExpression().get())};
}
<#else>
inline ${declarations.printVariableType(variable)} ${names.getter(variable)}() const {
  return ${names.name(variable)};
}
inline void ${names.setter(variable)}(const ${declarations.printVariableType(variable)} ${names.name(variable)}) {
  this->${names.name(variable)} = ${names.name(variable)};
}
</#if>


<#--
  Generates code that

  @param variable VariableSymbol
-->
${signature("variable")}
def< ${declarations.printVariableType(variable)} >(d, "${variable.getName()}", get_${variable.getName()}());

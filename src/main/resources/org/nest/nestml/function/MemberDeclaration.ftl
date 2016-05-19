<#--
  Generates C++ declaration for a variable

  @param variable VariableSymbol
  @result C++ declaration
-->
${signature("variable")}

${declarations.printVariableType(variable)} ${variable.getName()}; // ${variable.printComment()}


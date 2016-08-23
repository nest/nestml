<#--
  Generates C++ declaration for a variable

  @param variable VariableSymbol
  @result C++ declaration
-->
${signature("variable")}

${declarations.printVariableType(variable)} ${names.name(variable)}; // ${variable.printComment()}


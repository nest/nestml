<#--
  Generates C++ declaration for a variable

  @param var VariableSymbol
  @result C++ declaration
-->
${signature("var")}

${declarations.printVariableType(var)} ${var.getName()}_;


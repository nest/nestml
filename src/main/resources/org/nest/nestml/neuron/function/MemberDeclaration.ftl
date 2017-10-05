<#--
  Generates C++ declaration for a variable

  @param variable VariableSymbol
  @result C++ declaration
-->
${signature("variable")}
<#if variable.getComment().isPresent()>/** ${variable.getComment().get()} */</#if>
${declarations.printVariableType(variable)} ${names.name(variable)};
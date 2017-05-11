<#--
  Registers recordables for recording
  @param variable VariableSymbol
  @param names Helper class that maps symbols to C++ names
  @param declarations ASTDeclarations helper class

  @result C++ statement
-->
${signature("variable")}

<#assign varDomain = declarations.getDomainFromType(variable.getType())>

<#if varDomain == "double" && variable.isRecordable()>
insert_("${variable.getName()}", &${neuronName}::${names.getter(variable)});
</#if>

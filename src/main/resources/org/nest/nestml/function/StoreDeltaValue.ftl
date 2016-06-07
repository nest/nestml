<#--
  Computes the delta value between old variable value and new variable value and stores in a variable prefixed with
  'delta_'
-->

${signature("variable")}

${declarations.printVariableType(variable)} old_${variable.getName()} = P_.${variable.getName()};
updateValue<${declarations.printVariableType(variable)}>(d, "${variable.getName()}", P_.${variable.getName()});
${declarations.printVariableType(variable)} delta_${variable.getName()} = P_.${variable.getName()} - old_${variable.getName()};
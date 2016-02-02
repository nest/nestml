from sympy import *

<#compress>
    var('<#list variables as variable> ${variable.getName()} </#list>')
</#compress>

<#list aliases as alias>
outputFile = open('alias${alias.getName()}.expr', 'w')
tmp = str(simplify(solve(Eq(${printer.print(alias.getDeclaringExpression().get())}, ${alias.getName()}), ${dependentVariables[alias_index].getName()})))
tmp = tmp.replace('[', "(")
tmp = tmp.replace(']', ")")

outputFunction = "function set_${alias.getName()}(${dependentVariables[alias_index].getName()} ${dependentVariables[alias_index].getType().getName()}):" + str(tmp) + "\nend"
outputFile.write(outputFunction)
</#list>
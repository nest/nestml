from sympy import *

<#compress>
    var('<#list variables as variable> ${variable.getName()} </#list>')
</#compress>

<#list aliases as alias>
print(solve(Eq(${printer.print(alias.getDeclaringExpression().get())}, ${alias.getName()}), V))
</#list>
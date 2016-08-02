<#--
  Creates GSL implementation of the differentiation step for the system of ODEs.

  @result C++ Function
-->
<#assign ODEs = ast.getEquations()>
<#assign index = 0>
<#assign indexPostfix = "INDEX">

<#list ast.variablesDefinedByODE() as odeVariable>
const int ${odeVariable.getName()}_${indexPostfix} = ${index};
<#assign index = index + 1>
</#list>

extern "C" inline int
${simpleNeuronName}_dynamics( double, const double y[], double f[], void* pnode )
{
 // get access to node so we can almost work as in a member function
  assert( pnode );
  const ${simpleNeuronName}& node = *( reinterpret_cast< ${simpleNeuronName}* >( pnode ) );

  // y[] here is---and must be---the state vector supplied by the integrator,
  // not the state vector in the node, node.S_.y[].
  <#list body.getStateAliasSymbols() as alias>
    <#assign declaringExpression = odeTransformer.replaceSumCalls(alias.getDeclaringExpression().get())>
    double ${alias.getName()} = ${expressionsPrinterForGSL.print(declaringExpression)};
  </#list>

  <#list body.getParameterAliasSymbols() as alias>
    <#assign declaringExpression = odeTransformer.replaceSumCalls(alias.getDeclaringExpression().get())>
    double ${alias.getName()} = ${expressionsPrinterForGSL.print(declaringExpression)};
  </#list>

  <#list body.getODEAliases() as alias>
    <#assign declaringExpression = odeTransformer.replaceSumCalls(alias.getDeclaringExpression().get())>
    double ${alias.getName()} = ${expressionsPrinterForGSL.print(declaringExpression)};
  </#list>

  <#list ODEs as ode>
    <#assign simpleOde = odeTransformer.replaceSumCalls(ode)>
    f[ ${astUtils.convertToSimpleName(simpleOde.getLhs())}_${indexPostfix} ] = ${expressionsPrinterForGSL.print(simpleOde.getRhs())};
  </#list>

  return GSL_SUCCESS;
}



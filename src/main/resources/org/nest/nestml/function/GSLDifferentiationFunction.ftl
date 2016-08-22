<#--
  Creates GSL implementation of the differentiation step for the system of ODEs.

  @param ast ASTBody The body of the neuron containing ODE
  @result C++ Function
-->
<#assign ODEs = ast.getEquations()>
<#assign index = 0>
<#assign indexPostfix = "INDEX">

<#list ast.variablesDefinedByODE() as odeVariable>
const int ${names.name(odeVariable)}_${indexPostfix} = ${index};
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

  <#list ODEs as ode>
    <#assign simpleOde = odeTransformer.replaceSumCalls(ode)>
    <#list astUtils.getAliasSymbols(ode) as alias>
      <#if !alias.isInEquation()>
        <#assign declaringExpression = odeTransformer.replaceSumCalls(alias.getDeclaringExpression().get())>
        double ${names.name(alias)} = ${expressionsPrinterForGSL.print(declaringExpression)};
      </#if>
    </#list>
  </#list>

  <#list body.getODEAliases() as alias>
    <#assign declaringExpression = odeTransformer.replaceSumCalls(alias.getDeclaringExpression().get())>
    double ${names.name(alias)} = ${expressionsPrinterForGSL.print(declaringExpression)};
  </#list>

  <#list ast.variablesDefinedByODE() as odeVariable>
    <#assign simpleOde = odeTransformer.replaceSumCalls(odeVariable.getOdeDeclaration().get())>
    f[ ${names.name(odeVariable)}_${indexPostfix} ] = ${expressionsPrinterForGSL.print(simpleOde)};
  </#list>

  return GSL_SUCCESS;
}



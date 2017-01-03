<#--
  Creates GSL implementation of the differentiation step for the system of ODEs.

  @param ast ASTBody The body of the neuron containing ODE
  @result C++ Function
-->
extern "C" inline int
${simpleNeuronName}_dynamics( double, const double y[], double f[], void* pnode )
{
  typedef ${simpleNeuronName}::State_ State_;
  // get access to node so we can almost work as in a member function
  assert( pnode );
  const ${simpleNeuronName}& node = *( reinterpret_cast< ${simpleNeuronName}* >( pnode ) );

  // y[] here is---and must be---the state vector supplied by the integrator,
  // not the state vector in the node, node.S_.y[].

  <#list body.getODEBlock().get().getODEs() as ode>
    <#assign simpleOde = odeTransformer.replaceSumCalls(ode)>
    <#list astUtils.getAliasSymbols(ode) as function>
      <#if !function.isInEquation()>
        <#assign declaringExpression = odeTransformer.replaceSumCalls(function.getDeclaringExpression().get())>
        double ${names.name(function)} = ${expressionsPrinterForGSL.print(declaringExpression)};
      </#if>
    </#list>
  </#list>

  <#list body.getODEAliases() as function>
    <#assign declaringExpression = odeTransformer.replaceSumCalls(function.getDeclaringExpression().get())>
    double ${names.name(function)} = ${expressionsPrinterForGSL.print(declaringExpression)};
  </#list>

  <#list ast.variablesDefinedByODE() as odeVariable>
    <#assign simpleOde = odeTransformer.replaceSumCalls(odeVariable.getOdeDeclaration().get())>
    f[ ${names.arrayIndex(odeVariable)} ] = ${expressionsPrinterForGSL.print(simpleOde)};
  </#list>

  return GSL_SUCCESS;
}



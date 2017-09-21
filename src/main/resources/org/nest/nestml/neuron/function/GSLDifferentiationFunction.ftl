<#--
  Creates GSL implementation of the differentiation step for the system of ODEs.

  @param ast ASTBody The body of the neuron containing ODE
  @result C++ Function
-->
extern "C" inline int
${neuronName}_dynamics( double, const double ode_state[], double f[], void* pnode )
{
  typedef ${neuronName}::State_ State_;
  // get access to node so we can almost work as in a member function
  assert( pnode );
  const ${neuronName}& node = *( reinterpret_cast< ${neuronName}* >( pnode ) );

  // ode_state[] here is---and must be---the state vector supplied by the integrator,
  // not the state vector in the node, node.S_.ode_state[].

  <#list body.findEquationsBlock().get().getEquations() as ode>
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

  <#list ast.getNonFunctionInitialValuesSymbols() as odeVariable>
    <#assign simpleOde = odeTransformer.replaceSumCalls(odeVariable.getOdeDeclaration().get())>
    f[ ${names.arrayIndex(odeVariable)} ] = ${expressionsPrinterForGSL.print(simpleOde)};
  </#list>

  return GSL_SUCCESS;
}



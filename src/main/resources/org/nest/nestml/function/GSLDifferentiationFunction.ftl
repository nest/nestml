<#--
  Creates GSL implementation of the differentiation step for the system of ODEs.
  @grammar: OdeDeclaration  =
     "ODE" BLOCK_OPEN (NEWLINE)*
       (Eq (NEWLINE)*)*
       (ODE (NEWLINE)*)+
       BLOCK_CLOSE;
  @param ast ASTOdeDeclaration
  @param simpleNeuronName Name of the neuron
  @param tc templatecontroller
  @param ODEs List of odes form the
  @param nspPrefix List of odes form the
  @param expressionsPrinterForGSL Pretty printer for the GSL function calls
  @result C++ Function
-->

<#assign index = 0>
<#assign indexPostfix = "INDEX">
<#list ODEs as ode>
const int ${ode.getLhs()}_${indexPostfix} = ${index};
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
    <#list astUtils.getAliasSymbols(ode) as alias>
      double ${alias.getName()}
          = ${expressionsPrinterForGSL.print(alias.getDeclaringExpression().get())};
    </#list>
  </#list>

  <#list ODEs as ode>
    ${odeTransformer.replace_I_sum(ode)}
    f[ ${ode.getLhs()}_${indexPostfix} ] = ${expressionsPrinterForGSL.print(ode.getRhs())};
  </#list>

  return GSL_SUCCESS;
}



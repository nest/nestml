<#--
  Creates GSL implementation of the differentiation step for the system of ODEs.
  @grammar: OdeDeclaration  =
     "ODE" BLOCK_OPEN (NEWLINE)*
       (Eq (NEWLINE)*)*
       (ODE (NEWLINE)*)+
       BLOCK_CLOSE;
  @param ast ASTOdeDeclaration
  @param tc templatecontroller
  @result C++ Function
-->
<#assign index = 0>
<#assign indexPostfix = "INDEX">
<#list ODEs as ode>
const int ${ode.getLhsVariable()}_${indexPostfix} = ${index};
 <#assign index = index + 1>
</#list>
extern "C" inline int
${simpleNeuronName}Dynamics( double, const double y[], double f[], void* pnode )
{
 // get access to node so we can almost work as in a member function
  assert( pnode );
  const ${nspPrefix}::${simpleNeuronName}& node = *( reinterpret_cast< ${nspPrefix}::${simpleNeuronName}* >( pnode ) );

  // y[] here is---and must be---the state vector supplied by the integrator,
  // not the state vector in the node, node.S_.y[].

  <#list ODEs as ode>
    f[ ${ode.getLhsVariable()}_${indexPostfix} ] = ${expressionsPrinter.print(ode.getRhs())};
  </#list>

  return GSL_SUCCESS;
}



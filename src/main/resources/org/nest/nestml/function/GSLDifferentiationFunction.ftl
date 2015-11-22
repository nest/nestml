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
extern "C" inline int
${nspPrefix}::${simpleNeuronName}( double, const double y[], double f[], void* pnode )
{
 // get access to node so we can almost work as in a member function
  assert( pnode );
  const ${nspPrefix}::${simpleNeuronName}& node = *( reinterpret_cast< ${nspPrefix}::${simpleNeuronName}* >( pnode ) );

  // y[] here is---and must be---the state vector supplied by the integrator,
  // not the state vector in the node, node.S_.y[].

  // dV_m/dt
  f[ 0 ] = ( -I_leak - I_syn_exc - I_syn_inh + node.B_.I_stim_ + node.P_.I_e ) / node.P_.C_m;

  // d dg_exc/dt, dg_exc/dt
  f[ 1 ] = -y[ S::DG_EXC ] / node.P_.tau_synE;
  f[ 2 ] = y[ S::DG_EXC ] - ( y[ S::G_EXC ] / node.P_.tau_synE );

  // d dg_exc/dt, dg_exc/dt
  f[ 3 ] = -y[ S::DG_INH ] / node.P_.tau_synI;
  f[ 4 ] = y[ S::DG_INH ] - ( y[ S::G_INH ] / node.P_.tau_synI );

  return GSL_SUCCESS;
}



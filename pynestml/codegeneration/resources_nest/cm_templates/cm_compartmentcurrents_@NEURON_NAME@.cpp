#include "cm_compartmentcurrents_cm_default_nestml.h"






// Na channel //////////////////////////////////////////////////////////////////
nest::Na::Na()
// state variable m
: m_Na(0.0)
// state variable h
, h_Na(0.0)
// channel parameter gbar
,gbar_Na(0.0)
// channel parameter e
,e_Na(50.0){}

nest::Na::Na(const DictionaryDatum& channel_params)
// state variable m
: m_Na(0.0)
// state variable h
, h_Na(0.0)
// channel parameter gbar
,gbar_Na(0.0)
// channel parameter e
,e_Na(50.0)
// update Na channel parameters
{
    // Na channel parameter g_Na
    if( channel_params->known( "gbar_Na" ) )
        gbar_Na = getValue< double >( channel_params, "gbar_Na" );
    // Na channel parameter e_Na
    if( channel_params->known( "e_Na" ) )
        e_Na = getValue< double >( channel_params, "e_Na" );
}

void
nest::Na::append_recordables(std::map< Name, double* >* recordables,
                                               const long compartment_idx)
{
  // add state variables to recordables map
  ( *recordables )["m_Na" + std::to_string(compartment_idx)] = &m_Na;
  ( *recordables )["h_Na" + std::to_string(compartment_idx)] = &h_Na;
}

std::pair< double, double > nest::Na::f_numstep(const double v_comp)
{
    const double dt = Time::get_resolution().get_ms();

    double g_val = 0., i_val = 0.;
    if (gbar_Na > 1e-9)
    {
        
        // activation and timescale of state variable 'm'
        // inf
        double _m_inf_Na = m_inf_Na(v_comp);
        // tau
        double _tau_m_Na = tau_m_Na(v_comp);
        // activation and timescale of state variable 'h'
        // inf
        double _h_inf_Na = h_inf_Na(v_comp);
        // tau
        double _tau_h_Na = tau_h_Na(v_comp);

        
        // advance state variable m one timestep
        double p_m_Na = exp(-dt / _tau_m_Na); //
        m_Na *= p_m_Na ;
        m_Na += (1. - p_m_Na) * _m_inf_Na;
        // advance state variable h one timestep
        double p_h_Na = exp(-dt / _tau_h_Na); //
        h_Na *= p_h_Na ;
        h_Na += (1. - p_h_Na) * _h_inf_Na;

        
        // compute the conductance of the Na channel
        double i_tot = gbar_Na * pow(get_m_Na(), 3) * pow(get_h_Na(), 1) * (e_Na - get_v_comp());
        // derivative
        double d_i_tot_dv = (-(gbar_Na)) * get_h_Na() * pow(get_m_Na(), 3);

        // for numerical integration
        g_val = - d_i_tot_dv / 2.;
        i_val = i_tot - d_i_tot_dv * v_comp / 2.;
    }

    return std::make_pair(g_val, i_val);

}

//  functions Na
double nest::Na::m_inf_Na(double v_comp) const

{  
    return pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * pow((pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp) + pow((1.0 - 48.9271928701465 * std::exp(0.111111111111111 * v_comp)), ((-(1)))) * ((-(4.341612)) - 0.124 * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp);
}


//
double nest::Na::tau_m_Na(double v_comp) const

{  
    return 0.311526479750779 * pow((pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp) + pow((1.0 - 48.9271928701465 * std::exp(0.111111111111111 * v_comp)), ((-(1)))) * ((-(4.341612)) - 0.124 * v_comp)), ((-(1))));
}


//
double nest::Na::h_inf_Na(double v_comp) const

{  
    return 1.0 * pow((1.0 + 35734.4671267926 * std::exp(0.161290322580645 * v_comp)), ((-(1))));
}


//
double nest::Na::tau_h_Na(double v_comp) const

{  
    return 0.311526479750779 * pow((pow((1.0 - 4.52820432639598e-05 * std::exp((-(0.2)) * v_comp)), ((-(1)))) * (1.200312 + 0.024 * v_comp) + pow((1.0 - 3277527.87650153 * std::exp(0.2 * v_comp)), ((-(1)))) * ((-(0.6826183)) - 0.0091 * v_comp)), ((-(1))));
}




// K channel //////////////////////////////////////////////////////////////////
nest::K::K()
// state variable n
: n_K(0.0)
// channel parameter gbar
,gbar_K(0.0)
// channel parameter e
,e_K((-(85.0))){}

nest::K::K(const DictionaryDatum& channel_params)
// state variable n
: n_K(0.0)
// channel parameter gbar
,gbar_K(0.0)
// channel parameter e
,e_K((-(85.0)))
// update K channel parameters
{
    // K channel parameter g_K
    if( channel_params->known( "gbar_K" ) )
        gbar_K = getValue< double >( channel_params, "gbar_K" );
    // K channel parameter e_K
    if( channel_params->known( "e_K" ) )
        e_K = getValue< double >( channel_params, "e_K" );
}

void
nest::K::append_recordables(std::map< Name, double* >* recordables,
                                               const long compartment_idx)
{
  // add state variables to recordables map
  ( *recordables )["n_K" + std::to_string(compartment_idx)] = &n_K;
}

std::pair< double, double > nest::K::f_numstep(const double v_comp)
{
    const double dt = Time::get_resolution().get_ms();

    double g_val = 0., i_val = 0.;
    if (gbar_K > 1e-9)
    {
        
        // activation and timescale of state variable 'n'
        // inf
        double _n_inf_K = n_inf_K(v_comp);
        // tau
        double _tau_n_K = tau_n_K(v_comp);

        
        // advance state variable n one timestep
        double p_n_K = exp(-dt / _tau_n_K); //
        n_K *= p_n_K ;
        n_K += (1. - p_n_K) * _n_inf_K;

        
        // compute the conductance of the K channel
        double i_tot = gbar_K * get_n_K() * (e_K - get_v_comp());
        // derivative
        double d_i_tot_dv = (-(gbar_K)) * get_n_K();

        // for numerical integration
        g_val = - d_i_tot_dv / 2.;
        i_val = i_tot - d_i_tot_dv * v_comp / 2.;
    }

    return std::make_pair(g_val, i_val);

}

//  functions K
double nest::K::n_inf_K(double v_comp) const

{  
    return 0.02 * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1)))) * pow(((-(0.002)) * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * ((-(25.0)) + v_comp))), ((-(1)))) + 0.02 * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1))))), ((-(1)))) * ((-(25.0)) + v_comp);
}


//
double nest::K::tau_n_K(double v_comp) const

{  
    return 0.311526479750779 * pow(((-(0.002)) * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * ((-(25.0)) + v_comp))), ((-(1)))) + 0.02 * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1))))), ((-(1))));
}



////////////////////////////////////////////////////////////////////////////////
// AMPA synapse ////////////////////////////////////////////////////////////////
nest::AMPA::AMPA( const long syn_index )
    : tau_d_AMPA (3.0)
    , tau_r_AMPA (0.2)
    , e_AMPA (0)
{
  syn_idx = syn_index;
}

// AMPA synapse ////////////////////////////////////////////////////////////////
nest::AMPA::AMPA( const long syn_index, const DictionaryDatum& receptor_params )
    : tau_d_AMPA (3.0)
    , tau_r_AMPA (0.2)
    , e_AMPA (0)
{
  syn_idx = syn_index;

  // update parameters
  if( receptor_params->known( "tau_d_AMPA" ) )
    tau_d_AMPA = getValue< double >( receptor_params, "tau_d_AMPA" );
  if( receptor_params->known( "tau_r_AMPA" ) )
    tau_r_AMPA = getValue< double >( receptor_params, "tau_r_AMPA" );
  if( receptor_params->known( "e_AMPA" ) )
    e_AMPA = getValue< double >( receptor_params, "e_AMPA" );
}

void
nest::AMPA::append_recordables(std::map< Name, double* >* recordables)
{
  ( *recordables )["g_AMPA" + std::to_string(syn_idx)] = &g_AMPA__X__spikes_AMPA;
}

void nest::AMPA::calibrate()
{

  // initial values for user defined states
  // warning: this shadows class variables

  // set propagators to 0 initially, they will be set to proper value in numstep
  __P__g_AMPA__X__spikes_AMPA__g_AMPA__X__spikes_AMPA = 0;
  __P__g_AMPA__X__spikes_AMPA__g_AMPA__X__spikes_AMPA__d = 0;
  __P__g_AMPA__X__spikes_AMPA__d__g_AMPA__X__spikes_AMPA = 0;
  __P__g_AMPA__X__spikes_AMPA__d__g_AMPA__X__spikes_AMPA__d = 0;

  // initial values for kernel state variables, set to zero
  g_AMPA__X__spikes_AMPA = 0;
  g_AMPA__X__spikes_AMPA__d = 0;

  // user declared internals in order they were declared
  tp_AMPA = (tau_r_AMPA * tau_d_AMPA) / (tau_d_AMPA - tau_r_AMPA) * std::log(P_.tau_d_AMPA / P_.tau_r_AMPA);
  g_norm_AMPA = 1.0 / ((-(std::exp((-(V_.tp_AMPA)) / P_.tau_r_AMPA))) + std::exp((-(V_.tp_AMPA)) / P_.tau_d_AMPA));

  spikes_AMPA_->clear();
}

std::pair< double, double > nest::AMPA::f_numstep( const double v_comp, const long lag )
{
  const double __h = Time::get_resolution().get_ms();

  // set propagators to ode toolbox returned value
  __P__g_AMPA__X__spikes_AMPA__g_AMPA__X__spikes_AMPA = 1.0 * tau_d_AMPA * std::exp((-(V_.__h)) / P_.tau_d_AMPA) / (tau_d_AMPA - tau_r_AMPA) - 1.0 * tau_r_AMPA * std::exp((-(V_.__h)) / P_.tau_r_AMPA) / (tau_d_AMPA - tau_r_AMPA);
  __P__g_AMPA__X__spikes_AMPA__g_AMPA__X__spikes_AMPA__d = (-(1.0)) * tau_d_AMPA * tau_r_AMPA * std::exp((-(V_.__h)) / P_.tau_r_AMPA) / (tau_d_AMPA - tau_r_AMPA) + 1.0 * tau_d_AMPA * tau_r_AMPA * std::exp((-(V_.__h)) / P_.tau_d_AMPA) / (tau_d_AMPA - tau_r_AMPA);
  __P__g_AMPA__X__spikes_AMPA__d__g_AMPA__X__spikes_AMPA = 1.0 * std::exp((-(V_.__h)) / P_.tau_r_AMPA) / (tau_d_AMPA - tau_r_AMPA) - 1.0 * std::exp((-(V_.__h)) / P_.tau_d_AMPA) / (tau_d_AMPA - tau_r_AMPA);
  __P__g_AMPA__X__spikes_AMPA__d__g_AMPA__X__spikes_AMPA__d = 1.0 * tau_d_AMPA * std::exp((-(V_.__h)) / P_.tau_r_AMPA) / (tau_d_AMPA - tau_r_AMPA) - 1.0 * tau_r_AMPA * std::exp((-(V_.__h)) / P_.tau_d_AMPA) / (tau_d_AMPA - tau_r_AMPA);

  // get spikes
  double s_val = spikes_AMPA_->get_value( lag ); //  * g_norm_;

  // update kernel state variable / compute synaptic conductance
  g_AMPA__X__spikes_AMPA = __P__g_AMPA__X__spikes_AMPA__g_AMPA__X__spikes_AMPA * get_g_AMPA__X__spikes_AMPA() + __P__g_AMPA__X__spikes_AMPA__g_AMPA__X__spikes_AMPA__d * get_g_AMPA__X__spikes_AMPA__d();
  g_AMPA__X__spikes_AMPA += s_val * 0;
  g_AMPA__X__spikes_AMPA__d = __P__g_AMPA__X__spikes_AMPA__d__g_AMPA__X__spikes_AMPA * get_g_AMPA__X__spikes_AMPA() + __P__g_AMPA__X__spikes_AMPA__d__g_AMPA__X__spikes_AMPA__d * get_g_AMPA__X__spikes_AMPA__d();
  g_AMPA__X__spikes_AMPA__d += s_val * g_norm_AMPA * (1 / tau_r_AMPA - 1 / tau_d_AMPA);

  // total current
  // this expression should be the transformed inline expression
  double i_tot = get_g_AMPA__X__spikes_AMPA() * (e_AMPA - get_v_comp());

  // derivative of that expression
  // voltage derivative of total current
  // compute derivative with respect to current with sympy
  double d_i_tot_dv = (-(get_g_AMPA__X__spikes_AMPA()));

  // for numerical integration
  double g_val = - d_i_tot_dv / 2.;
  double i_val = i_tot - d_i_tot_dv * v_comp / 2.;

  return std::make_pair(g_val, i_val);

}
//  functions K
double nest::AMPA::n_inf_K(double v_comp) const

{  
    return 0.02 * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1)))) * pow(((-(0.002)) * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * ((-(25.0)) + v_comp))), ((-(1)))) + 0.02 * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1))))), ((-(1)))) * ((-(25.0)) + v_comp);
}
//
double nest::AMPA::tau_n_K(double v_comp) const

{  
    return 0.311526479750779 * pow(((-(0.002)) * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * ((-(25.0)) + v_comp))), ((-(1)))) + 0.02 * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1))))), ((-(1))));
}
//  functions Na
double nest::AMPA::m_inf_Na(double v_comp) const

{  
    return pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * pow((pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp) + pow((1.0 - 48.9271928701465 * std::exp(0.111111111111111 * v_comp)), ((-(1)))) * ((-(4.341612)) - 0.124 * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp);
}
//
double nest::AMPA::tau_m_Na(double v_comp) const

{  
    return 0.311526479750779 * pow((pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp) + pow((1.0 - 48.9271928701465 * std::exp(0.111111111111111 * v_comp)), ((-(1)))) * ((-(4.341612)) - 0.124 * v_comp)), ((-(1))));
}
//
double nest::AMPA::h_inf_Na(double v_comp) const

{  
    return 1.0 * pow((1.0 + 35734.4671267926 * std::exp(0.161290322580645 * v_comp)), ((-(1))));
}
//
double nest::AMPA::tau_h_Na(double v_comp) const

{  
    return 0.311526479750779 * pow((pow((1.0 - 4.52820432639598e-05 * std::exp((-(0.2)) * v_comp)), ((-(1)))) * (1.200312 + 0.024 * v_comp) + pow((1.0 - 3277527.87650153 * std::exp(0.2 * v_comp)), ((-(1)))) * ((-(0.6826183)) - 0.0091 * v_comp)), ((-(1))));
}

// AMPA synapse end ///////////////////////////////////////////////////////////
// GABA synapse ////////////////////////////////////////////////////////////////
nest::GABA::GABA( const long syn_index )
    : tau_r_GABA (0.2)
    , tau_d_GABA (10.0)
    , e_GABA ((-(80.0)))
{
  syn_idx = syn_index;
}

// GABA synapse ////////////////////////////////////////////////////////////////
nest::GABA::GABA( const long syn_index, const DictionaryDatum& receptor_params )
    : tau_r_GABA (0.2)
    , tau_d_GABA (10.0)
    , e_GABA ((-(80.0)))
{
  syn_idx = syn_index;

  // update parameters
  if( receptor_params->known( "tau_r_GABA" ) )
    tau_r_GABA = getValue< double >( receptor_params, "tau_r_GABA" );
  if( receptor_params->known( "tau_d_GABA" ) )
    tau_d_GABA = getValue< double >( receptor_params, "tau_d_GABA" );
  if( receptor_params->known( "e_GABA" ) )
    e_GABA = getValue< double >( receptor_params, "e_GABA" );
}

void
nest::GABA::append_recordables(std::map< Name, double* >* recordables)
{
  ( *recordables )["g_GABA" + std::to_string(syn_idx)] = &g_GABA__X__spikes_GABA;
}

void nest::GABA::calibrate()
{

  // initial values for user defined states
  // warning: this shadows class variables

  // set propagators to 0 initially, they will be set to proper value in numstep
  __P__g_GABA__X__spikes_GABA__g_GABA__X__spikes_GABA = 0;
  __P__g_GABA__X__spikes_GABA__g_GABA__X__spikes_GABA__d = 0;
  __P__g_GABA__X__spikes_GABA__d__g_GABA__X__spikes_GABA = 0;
  __P__g_GABA__X__spikes_GABA__d__g_GABA__X__spikes_GABA__d = 0;

  // initial values for kernel state variables, set to zero
  g_GABA__X__spikes_GABA = 0;
  g_GABA__X__spikes_GABA__d = 0;

  // user declared internals in order they were declared
  tp_GABA = (tau_r_GABA * tau_d_GABA) / (tau_d_GABA - tau_r_GABA) * std::log(P_.tau_d_GABA / P_.tau_r_GABA);
  g_norm_GABA = 1.0 / ((-(std::exp((-(V_.tp_GABA)) / P_.tau_r_GABA))) + std::exp((-(V_.tp_GABA)) / P_.tau_d_GABA));

  spikes_GABA_->clear();
}

std::pair< double, double > nest::GABA::f_numstep( const double v_comp, const long lag )
{
  const double __h = Time::get_resolution().get_ms();

  // set propagators to ode toolbox returned value
  __P__g_GABA__X__spikes_GABA__g_GABA__X__spikes_GABA = 1.0 * tau_d_GABA * std::exp((-(V_.__h)) / P_.tau_d_GABA) / (tau_d_GABA - tau_r_GABA) - 1.0 * tau_r_GABA * std::exp((-(V_.__h)) / P_.tau_r_GABA) / (tau_d_GABA - tau_r_GABA);
  __P__g_GABA__X__spikes_GABA__g_GABA__X__spikes_GABA__d = (-(1.0)) * tau_d_GABA * tau_r_GABA * std::exp((-(V_.__h)) / P_.tau_r_GABA) / (tau_d_GABA - tau_r_GABA) + 1.0 * tau_d_GABA * tau_r_GABA * std::exp((-(V_.__h)) / P_.tau_d_GABA) / (tau_d_GABA - tau_r_GABA);
  __P__g_GABA__X__spikes_GABA__d__g_GABA__X__spikes_GABA = 1.0 * std::exp((-(V_.__h)) / P_.tau_r_GABA) / (tau_d_GABA - tau_r_GABA) - 1.0 * std::exp((-(V_.__h)) / P_.tau_d_GABA) / (tau_d_GABA - tau_r_GABA);
  __P__g_GABA__X__spikes_GABA__d__g_GABA__X__spikes_GABA__d = 1.0 * tau_d_GABA * std::exp((-(V_.__h)) / P_.tau_r_GABA) / (tau_d_GABA - tau_r_GABA) - 1.0 * tau_r_GABA * std::exp((-(V_.__h)) / P_.tau_d_GABA) / (tau_d_GABA - tau_r_GABA);

  // get spikes
  double s_val = spikes_GABA_->get_value( lag ); //  * g_norm_;

  // update kernel state variable / compute synaptic conductance
  g_GABA__X__spikes_GABA = __P__g_GABA__X__spikes_GABA__g_GABA__X__spikes_GABA * get_g_GABA__X__spikes_GABA() + __P__g_GABA__X__spikes_GABA__g_GABA__X__spikes_GABA__d * get_g_GABA__X__spikes_GABA__d();
  g_GABA__X__spikes_GABA += s_val * 0;
  g_GABA__X__spikes_GABA__d = __P__g_GABA__X__spikes_GABA__d__g_GABA__X__spikes_GABA * get_g_GABA__X__spikes_GABA() + __P__g_GABA__X__spikes_GABA__d__g_GABA__X__spikes_GABA__d * get_g_GABA__X__spikes_GABA__d();
  g_GABA__X__spikes_GABA__d += s_val * g_norm_GABA * (1 / tau_r_GABA - 1 / tau_d_GABA);

  // total current
  // this expression should be the transformed inline expression
  double i_tot = get_g_GABA__X__spikes_GABA() * (e_GABA - get_v_comp());

  // derivative of that expression
  // voltage derivative of total current
  // compute derivative with respect to current with sympy
  double d_i_tot_dv = (-(get_g_GABA__X__spikes_GABA()));

  // for numerical integration
  double g_val = - d_i_tot_dv / 2.;
  double i_val = i_tot - d_i_tot_dv * v_comp / 2.;

  return std::make_pair(g_val, i_val);

}
//  functions K
double nest::GABA::n_inf_K(double v_comp) const

{  
    return 0.02 * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1)))) * pow(((-(0.002)) * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * ((-(25.0)) + v_comp))), ((-(1)))) + 0.02 * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1))))), ((-(1)))) * ((-(25.0)) + v_comp);
}
//
double nest::GABA::tau_n_K(double v_comp) const

{  
    return 0.311526479750779 * pow(((-(0.002)) * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * ((-(25.0)) + v_comp))), ((-(1)))) + 0.02 * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1))))), ((-(1))));
}
//  functions Na
double nest::GABA::m_inf_Na(double v_comp) const

{  
    return pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * pow((pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp) + pow((1.0 - 48.9271928701465 * std::exp(0.111111111111111 * v_comp)), ((-(1)))) * ((-(4.341612)) - 0.124 * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp);
}
//
double nest::GABA::tau_m_Na(double v_comp) const

{  
    return 0.311526479750779 * pow((pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp) + pow((1.0 - 48.9271928701465 * std::exp(0.111111111111111 * v_comp)), ((-(1)))) * ((-(4.341612)) - 0.124 * v_comp)), ((-(1))));
}
//
double nest::GABA::h_inf_Na(double v_comp) const

{  
    return 1.0 * pow((1.0 + 35734.4671267926 * std::exp(0.161290322580645 * v_comp)), ((-(1))));
}
//
double nest::GABA::tau_h_Na(double v_comp) const

{  
    return 0.311526479750779 * pow((pow((1.0 - 4.52820432639598e-05 * std::exp((-(0.2)) * v_comp)), ((-(1)))) * (1.200312 + 0.024 * v_comp) + pow((1.0 - 3277527.87650153 * std::exp(0.2 * v_comp)), ((-(1)))) * ((-(0.6826183)) - 0.0091 * v_comp)), ((-(1))));
}

// GABA synapse end ///////////////////////////////////////////////////////////
// NMDA synapse ////////////////////////////////////////////////////////////////
nest::NMDA::NMDA( const long syn_index )
    : e_NMDA (0)
    , tau_d_NMDA (43.0)
    , tau_r_NMDA (0.2)
{
  syn_idx = syn_index;
}

// NMDA synapse ////////////////////////////////////////////////////////////////
nest::NMDA::NMDA( const long syn_index, const DictionaryDatum& receptor_params )
    : e_NMDA (0)
    , tau_d_NMDA (43.0)
    , tau_r_NMDA (0.2)
{
  syn_idx = syn_index;

  // update parameters
  if( receptor_params->known( "e_NMDA" ) )
    e_NMDA = getValue< double >( receptor_params, "e_NMDA" );
  if( receptor_params->known( "tau_d_NMDA" ) )
    tau_d_NMDA = getValue< double >( receptor_params, "tau_d_NMDA" );
  if( receptor_params->known( "tau_r_NMDA" ) )
    tau_r_NMDA = getValue< double >( receptor_params, "tau_r_NMDA" );
}

void
nest::NMDA::append_recordables(std::map< Name, double* >* recordables)
{
  ( *recordables )["g_NMDA" + std::to_string(syn_idx)] = &g_NMDA__X__spikes_NMDA;
}

void nest::NMDA::calibrate()
{

  // initial values for user defined states
  // warning: this shadows class variables

  // set propagators to 0 initially, they will be set to proper value in numstep
  __P__g_NMDA__X__spikes_NMDA__g_NMDA__X__spikes_NMDA = 0;
  __P__g_NMDA__X__spikes_NMDA__g_NMDA__X__spikes_NMDA__d = 0;
  __P__g_NMDA__X__spikes_NMDA__d__g_NMDA__X__spikes_NMDA = 0;
  __P__g_NMDA__X__spikes_NMDA__d__g_NMDA__X__spikes_NMDA__d = 0;

  // initial values for kernel state variables, set to zero
  g_NMDA__X__spikes_NMDA = 0;
  g_NMDA__X__spikes_NMDA__d = 0;

  // user declared internals in order they were declared
  tp_NMDA = (tau_r_NMDA * tau_d_NMDA) / (tau_d_NMDA - tau_r_NMDA) * std::log(P_.tau_d_NMDA / P_.tau_r_NMDA);
  g_norm_NMDA = 1.0 / ((-(std::exp((-(V_.tp_NMDA)) / P_.tau_r_NMDA))) + std::exp((-(V_.tp_NMDA)) / P_.tau_d_NMDA));

  spikes_NMDA_->clear();
}

std::pair< double, double > nest::NMDA::f_numstep( const double v_comp, const long lag )
{
  const double __h = Time::get_resolution().get_ms();

  // set propagators to ode toolbox returned value
  __P__g_NMDA__X__spikes_NMDA__g_NMDA__X__spikes_NMDA = 1.0 * tau_d_NMDA * std::exp((-(V_.__h)) / P_.tau_d_NMDA) / (tau_d_NMDA - tau_r_NMDA) - 1.0 * tau_r_NMDA * std::exp((-(V_.__h)) / P_.tau_r_NMDA) / (tau_d_NMDA - tau_r_NMDA);
  __P__g_NMDA__X__spikes_NMDA__g_NMDA__X__spikes_NMDA__d = (-(1.0)) * tau_d_NMDA * tau_r_NMDA * std::exp((-(V_.__h)) / P_.tau_r_NMDA) / (tau_d_NMDA - tau_r_NMDA) + 1.0 * tau_d_NMDA * tau_r_NMDA * std::exp((-(V_.__h)) / P_.tau_d_NMDA) / (tau_d_NMDA - tau_r_NMDA);
  __P__g_NMDA__X__spikes_NMDA__d__g_NMDA__X__spikes_NMDA = 1.0 * std::exp((-(V_.__h)) / P_.tau_r_NMDA) / (tau_d_NMDA - tau_r_NMDA) - 1.0 * std::exp((-(V_.__h)) / P_.tau_d_NMDA) / (tau_d_NMDA - tau_r_NMDA);
  __P__g_NMDA__X__spikes_NMDA__d__g_NMDA__X__spikes_NMDA__d = 1.0 * tau_d_NMDA * std::exp((-(V_.__h)) / P_.tau_r_NMDA) / (tau_d_NMDA - tau_r_NMDA) - 1.0 * tau_r_NMDA * std::exp((-(V_.__h)) / P_.tau_d_NMDA) / (tau_d_NMDA - tau_r_NMDA);

  // get spikes
  double s_val = spikes_NMDA_->get_value( lag ); //  * g_norm_;

  // update kernel state variable / compute synaptic conductance
  g_NMDA__X__spikes_NMDA = __P__g_NMDA__X__spikes_NMDA__g_NMDA__X__spikes_NMDA * get_g_NMDA__X__spikes_NMDA() + __P__g_NMDA__X__spikes_NMDA__g_NMDA__X__spikes_NMDA__d * get_g_NMDA__X__spikes_NMDA__d();
  g_NMDA__X__spikes_NMDA += s_val * 0;
  g_NMDA__X__spikes_NMDA__d = __P__g_NMDA__X__spikes_NMDA__d__g_NMDA__X__spikes_NMDA * get_g_NMDA__X__spikes_NMDA() + __P__g_NMDA__X__spikes_NMDA__d__g_NMDA__X__spikes_NMDA__d * get_g_NMDA__X__spikes_NMDA__d();
  g_NMDA__X__spikes_NMDA__d += s_val * g_norm_NMDA * (1 / tau_r_NMDA - 1 / tau_d_NMDA);

  // total current
  // this expression should be the transformed inline expression
  double i_tot = get_g_NMDA__X__spikes_NMDA() * (e_NMDA - get_v_comp()) / (1.0 + 0.3 * std::exp((-(0.1)) * get_v_comp()));

  // derivative of that expression
  // voltage derivative of total current
  // compute derivative with respect to current with sympy
  double d_i_tot_dv = (-(get_g_NMDA__X__spikes_NMDA())) / (1.0 + 0.3 * std::exp((-(0.1)) * get_v_comp())) + 0.03 * get_g_NMDA__X__spikes_NMDA() * (e_NMDA - get_v_comp()) * std::exp((-(0.1)) * get_v_comp()) / pow((1.0 + 0.3 * std::exp((-(0.1)) * get_v_comp())), 2);

  // for numerical integration
  double g_val = - d_i_tot_dv / 2.;
  double i_val = i_tot - d_i_tot_dv * v_comp / 2.;

  return std::make_pair(g_val, i_val);

}
//  functions K
double nest::NMDA::n_inf_K(double v_comp) const

{  
    return 0.02 * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1)))) * pow(((-(0.002)) * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * ((-(25.0)) + v_comp))), ((-(1)))) + 0.02 * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1))))), ((-(1)))) * ((-(25.0)) + v_comp);
}
//
double nest::NMDA::tau_n_K(double v_comp) const

{  
    return 0.311526479750779 * pow(((-(0.002)) * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * ((-(25.0)) + v_comp))), ((-(1)))) + 0.02 * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1))))), ((-(1))));
}
//  functions Na
double nest::NMDA::m_inf_Na(double v_comp) const

{  
    return pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * pow((pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp) + pow((1.0 - 48.9271928701465 * std::exp(0.111111111111111 * v_comp)), ((-(1)))) * ((-(4.341612)) - 0.124 * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp);
}
//
double nest::NMDA::tau_m_Na(double v_comp) const

{  
    return 0.311526479750779 * pow((pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp) + pow((1.0 - 48.9271928701465 * std::exp(0.111111111111111 * v_comp)), ((-(1)))) * ((-(4.341612)) - 0.124 * v_comp)), ((-(1))));
}
//
double nest::NMDA::h_inf_Na(double v_comp) const

{  
    return 1.0 * pow((1.0 + 35734.4671267926 * std::exp(0.161290322580645 * v_comp)), ((-(1))));
}
//
double nest::NMDA::tau_h_Na(double v_comp) const

{  
    return 0.311526479750779 * pow((pow((1.0 - 4.52820432639598e-05 * std::exp((-(0.2)) * v_comp)), ((-(1)))) * (1.200312 + 0.024 * v_comp) + pow((1.0 - 3277527.87650153 * std::exp(0.2 * v_comp)), ((-(1)))) * ((-(0.6826183)) - 0.0091 * v_comp)), ((-(1))));
}

// NMDA synapse end ///////////////////////////////////////////////////////////
// AMPA_NMDA synapse ////////////////////////////////////////////////////////////////
nest::AMPA_NMDA::AMPA_NMDA( const long syn_index )
    : tau_d_AN_NMDA (43.0)
    , tau_r_AN_NMDA (0.2)
    , NMDA_ratio (2.0)
    , tau_r_AN_AMPA (0.2)
    , e_AN_AMPA (0)
    , tau_d_AN_AMPA (3.0)
    , e_AN_NMDA (0)
{
  syn_idx = syn_index;
}

// AMPA_NMDA synapse ////////////////////////////////////////////////////////////////
nest::AMPA_NMDA::AMPA_NMDA( const long syn_index, const DictionaryDatum& receptor_params )
    : tau_d_AN_NMDA (43.0)
    , tau_r_AN_NMDA (0.2)
    , NMDA_ratio (2.0)
    , tau_r_AN_AMPA (0.2)
    , e_AN_AMPA (0)
    , tau_d_AN_AMPA (3.0)
    , e_AN_NMDA (0)
{
  syn_idx = syn_index;

  // update parameters
  if( receptor_params->known( "tau_d_AN_NMDA" ) )
    tau_d_AN_NMDA = getValue< double >( receptor_params, "tau_d_AN_NMDA" );
  if( receptor_params->known( "tau_r_AN_NMDA" ) )
    tau_r_AN_NMDA = getValue< double >( receptor_params, "tau_r_AN_NMDA" );
  if( receptor_params->known( "NMDA_ratio" ) )
    NMDA_ratio = getValue< double >( receptor_params, "NMDA_ratio" );
  if( receptor_params->known( "tau_r_AN_AMPA" ) )
    tau_r_AN_AMPA = getValue< double >( receptor_params, "tau_r_AN_AMPA" );
  if( receptor_params->known( "e_AN_AMPA" ) )
    e_AN_AMPA = getValue< double >( receptor_params, "e_AN_AMPA" );
  if( receptor_params->known( "tau_d_AN_AMPA" ) )
    tau_d_AN_AMPA = getValue< double >( receptor_params, "tau_d_AN_AMPA" );
  if( receptor_params->known( "e_AN_NMDA" ) )
    e_AN_NMDA = getValue< double >( receptor_params, "e_AN_NMDA" );
}

void
nest::AMPA_NMDA::append_recordables(std::map< Name, double* >* recordables)
{
  ( *recordables )["g_AN_NMDA" + std::to_string(syn_idx)] = &g_AN_NMDA__X__spikes_AN;
  ( *recordables )["g_AN_AMPA" + std::to_string(syn_idx)] = &g_AN_AMPA__X__spikes_AN;
}

void nest::AMPA_NMDA::calibrate()
{

  // initial values for user defined states
  // warning: this shadows class variables

  // set propagators to 0 initially, they will be set to proper value in numstep
  __P__g_AN_NMDA__X__spikes_AN__g_AN_NMDA__X__spikes_AN = 0;
  __P__g_AN_NMDA__X__spikes_AN__g_AN_NMDA__X__spikes_AN__d = 0;
  __P__g_AN_NMDA__X__spikes_AN__d__g_AN_NMDA__X__spikes_AN = 0;
  __P__g_AN_NMDA__X__spikes_AN__d__g_AN_NMDA__X__spikes_AN__d = 0;
  __P__g_AN_AMPA__X__spikes_AN__g_AN_AMPA__X__spikes_AN = 0;
  __P__g_AN_AMPA__X__spikes_AN__g_AN_AMPA__X__spikes_AN__d = 0;
  __P__g_AN_AMPA__X__spikes_AN__d__g_AN_AMPA__X__spikes_AN = 0;
  __P__g_AN_AMPA__X__spikes_AN__d__g_AN_AMPA__X__spikes_AN__d = 0;

  // initial values for kernel state variables, set to zero
  g_AN_NMDA__X__spikes_AN = 0;
  g_AN_NMDA__X__spikes_AN__d = 0;
  g_AN_AMPA__X__spikes_AN = 0;
  g_AN_AMPA__X__spikes_AN__d = 0;

  // user declared internals in order they were declared
  tp_AN_AMPA = (tau_r_AN_AMPA * tau_d_AN_AMPA) / (tau_d_AN_AMPA - tau_r_AN_AMPA) * std::log(P_.tau_d_AN_AMPA / P_.tau_r_AN_AMPA);
  g_norm_AN_AMPA = 1.0 / ((-(std::exp((-(V_.tp_AN_AMPA)) / P_.tau_r_AN_AMPA))) + std::exp((-(V_.tp_AN_AMPA)) / P_.tau_d_AN_AMPA));
  tp_AN_NMDA = (tau_r_AN_NMDA * tau_d_AN_NMDA) / (tau_d_AN_NMDA - tau_r_AN_NMDA) * std::log(P_.tau_d_AN_NMDA / P_.tau_r_AN_NMDA);
  g_norm_AN_NMDA = 1.0 / ((-(std::exp((-(V_.tp_AN_NMDA)) / P_.tau_r_AN_NMDA))) + std::exp((-(V_.tp_AN_NMDA)) / P_.tau_d_AN_NMDA));

  spikes_AN_->clear();
}

std::pair< double, double > nest::AMPA_NMDA::f_numstep( const double v_comp, const long lag )
{
  const double __h = Time::get_resolution().get_ms();

  // set propagators to ode toolbox returned value
  __P__g_AN_NMDA__X__spikes_AN__g_AN_NMDA__X__spikes_AN = 1.0 * tau_d_AN_NMDA * std::exp((-(V_.__h)) / P_.tau_d_AN_NMDA) / (tau_d_AN_NMDA - tau_r_AN_NMDA) - 1.0 * tau_r_AN_NMDA * std::exp((-(V_.__h)) / P_.tau_r_AN_NMDA) / (tau_d_AN_NMDA - tau_r_AN_NMDA);
  __P__g_AN_NMDA__X__spikes_AN__g_AN_NMDA__X__spikes_AN__d = (-(1.0)) * tau_d_AN_NMDA * tau_r_AN_NMDA * std::exp((-(V_.__h)) / P_.tau_r_AN_NMDA) / (tau_d_AN_NMDA - tau_r_AN_NMDA) + 1.0 * tau_d_AN_NMDA * tau_r_AN_NMDA * std::exp((-(V_.__h)) / P_.tau_d_AN_NMDA) / (tau_d_AN_NMDA - tau_r_AN_NMDA);
  __P__g_AN_NMDA__X__spikes_AN__d__g_AN_NMDA__X__spikes_AN = 1.0 * std::exp((-(V_.__h)) / P_.tau_r_AN_NMDA) / (tau_d_AN_NMDA - tau_r_AN_NMDA) - 1.0 * std::exp((-(V_.__h)) / P_.tau_d_AN_NMDA) / (tau_d_AN_NMDA - tau_r_AN_NMDA);
  __P__g_AN_NMDA__X__spikes_AN__d__g_AN_NMDA__X__spikes_AN__d = 1.0 * tau_d_AN_NMDA * std::exp((-(V_.__h)) / P_.tau_r_AN_NMDA) / (tau_d_AN_NMDA - tau_r_AN_NMDA) - 1.0 * tau_r_AN_NMDA * std::exp((-(V_.__h)) / P_.tau_d_AN_NMDA) / (tau_d_AN_NMDA - tau_r_AN_NMDA);
  __P__g_AN_AMPA__X__spikes_AN__g_AN_AMPA__X__spikes_AN = 1.0 * tau_d_AN_AMPA * std::exp((-(V_.__h)) / P_.tau_d_AN_AMPA) / (tau_d_AN_AMPA - tau_r_AN_AMPA) - 1.0 * tau_r_AN_AMPA * std::exp((-(V_.__h)) / P_.tau_r_AN_AMPA) / (tau_d_AN_AMPA - tau_r_AN_AMPA);
  __P__g_AN_AMPA__X__spikes_AN__g_AN_AMPA__X__spikes_AN__d = (-(1.0)) * tau_d_AN_AMPA * tau_r_AN_AMPA * std::exp((-(V_.__h)) / P_.tau_r_AN_AMPA) / (tau_d_AN_AMPA - tau_r_AN_AMPA) + 1.0 * tau_d_AN_AMPA * tau_r_AN_AMPA * std::exp((-(V_.__h)) / P_.tau_d_AN_AMPA) / (tau_d_AN_AMPA - tau_r_AN_AMPA);
  __P__g_AN_AMPA__X__spikes_AN__d__g_AN_AMPA__X__spikes_AN = 1.0 * std::exp((-(V_.__h)) / P_.tau_r_AN_AMPA) / (tau_d_AN_AMPA - tau_r_AN_AMPA) - 1.0 * std::exp((-(V_.__h)) / P_.tau_d_AN_AMPA) / (tau_d_AN_AMPA - tau_r_AN_AMPA);
  __P__g_AN_AMPA__X__spikes_AN__d__g_AN_AMPA__X__spikes_AN__d = 1.0 * tau_d_AN_AMPA * std::exp((-(V_.__h)) / P_.tau_r_AN_AMPA) / (tau_d_AN_AMPA - tau_r_AN_AMPA) - 1.0 * tau_r_AN_AMPA * std::exp((-(V_.__h)) / P_.tau_d_AN_AMPA) / (tau_d_AN_AMPA - tau_r_AN_AMPA);

  // get spikes
  double s_val = spikes_AN_->get_value( lag ); //  * g_norm_;

  // update kernel state variable / compute synaptic conductance
  g_AN_NMDA__X__spikes_AN = __P__g_AN_NMDA__X__spikes_AN__g_AN_NMDA__X__spikes_AN * get_g_AN_NMDA__X__spikes_AN() + __P__g_AN_NMDA__X__spikes_AN__g_AN_NMDA__X__spikes_AN__d * get_g_AN_NMDA__X__spikes_AN__d();
  g_AN_NMDA__X__spikes_AN += s_val * 0;
  g_AN_NMDA__X__spikes_AN__d = __P__g_AN_NMDA__X__spikes_AN__d__g_AN_NMDA__X__spikes_AN * get_g_AN_NMDA__X__spikes_AN() + __P__g_AN_NMDA__X__spikes_AN__d__g_AN_NMDA__X__spikes_AN__d * get_g_AN_NMDA__X__spikes_AN__d();
  g_AN_NMDA__X__spikes_AN__d += s_val * g_norm_AN_NMDA * (1 / tau_r_AN_NMDA - 1 / tau_d_AN_NMDA);
  g_AN_AMPA__X__spikes_AN = __P__g_AN_AMPA__X__spikes_AN__g_AN_AMPA__X__spikes_AN * get_g_AN_AMPA__X__spikes_AN() + __P__g_AN_AMPA__X__spikes_AN__g_AN_AMPA__X__spikes_AN__d * get_g_AN_AMPA__X__spikes_AN__d();
  g_AN_AMPA__X__spikes_AN += s_val * 0;
  g_AN_AMPA__X__spikes_AN__d = __P__g_AN_AMPA__X__spikes_AN__d__g_AN_AMPA__X__spikes_AN * get_g_AN_AMPA__X__spikes_AN() + __P__g_AN_AMPA__X__spikes_AN__d__g_AN_AMPA__X__spikes_AN__d * get_g_AN_AMPA__X__spikes_AN__d();
  g_AN_AMPA__X__spikes_AN__d += s_val * g_norm_AN_AMPA * (1 / tau_r_AN_AMPA - 1 / tau_d_AN_AMPA);

  // total current
  // this expression should be the transformed inline expression
  double i_tot = get_g_AN_AMPA__X__spikes_AN() * (e_AN_AMPA - get_v_comp()) + NMDA_ratio * get_g_AN_NMDA__X__spikes_AN() * (e_AN_NMDA - get_v_comp()) / (1.0 + 0.3 * std::exp((-(0.1)) * get_v_comp()));

  // derivative of that expression
  // voltage derivative of total current
  // compute derivative with respect to current with sympy
  double d_i_tot_dv = (-(NMDA_ratio)) * get_g_AN_NMDA__X__spikes_AN() / (1.0 + 0.3 * std::exp((-(0.1)) * get_v_comp())) + 0.03 * NMDA_ratio * get_g_AN_NMDA__X__spikes_AN() * (e_AN_NMDA - get_v_comp()) * std::exp((-(0.1)) * get_v_comp()) / pow((1.0 + 0.3 * std::exp((-(0.1)) * get_v_comp())), 2) - get_g_AN_AMPA__X__spikes_AN();

  // for numerical integration
  double g_val = - d_i_tot_dv / 2.;
  double i_val = i_tot - d_i_tot_dv * v_comp / 2.;

  return std::make_pair(g_val, i_val);

}
//  functions K
double nest::AMPA_NMDA::n_inf_K(double v_comp) const

{  
    return 0.02 * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1)))) * pow(((-(0.002)) * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * ((-(25.0)) + v_comp))), ((-(1)))) + 0.02 * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1))))), ((-(1)))) * ((-(25.0)) + v_comp);
}
//
double nest::AMPA_NMDA::tau_n_K(double v_comp) const

{  
    return 0.311526479750779 * pow(((-(0.002)) * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * ((-(25.0)) + v_comp))), ((-(1)))) + 0.02 * ((-(25.0)) + v_comp) * pow((1.0 - std::exp(0.111111111111111 * (25.0 - v_comp))), ((-(1))))), ((-(1))));
}
//  functions Na
double nest::AMPA_NMDA::m_inf_Na(double v_comp) const

{  
    return pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * pow((pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp) + pow((1.0 - 48.9271928701465 * std::exp(0.111111111111111 * v_comp)), ((-(1)))) * ((-(4.341612)) - 0.124 * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp);
}
//
double nest::AMPA_NMDA::tau_m_Na(double v_comp) const

{  
    return 0.311526479750779 * pow((pow((1.0 - 0.020438532058318 * std::exp((-(0.111111111111111)) * v_comp)), ((-(1)))) * (6.372366 + 0.182 * v_comp) + pow((1.0 - 48.9271928701465 * std::exp(0.111111111111111 * v_comp)), ((-(1)))) * ((-(4.341612)) - 0.124 * v_comp)), ((-(1))));
}
//
double nest::AMPA_NMDA::h_inf_Na(double v_comp) const

{  
    return 1.0 * pow((1.0 + 35734.4671267926 * std::exp(0.161290322580645 * v_comp)), ((-(1))));
}
//
double nest::AMPA_NMDA::tau_h_Na(double v_comp) const

{  
    return 0.311526479750779 * pow((pow((1.0 - 4.52820432639598e-05 * std::exp((-(0.2)) * v_comp)), ((-(1)))) * (1.200312 + 0.024 * v_comp) + pow((1.0 - 3277527.87650153 * std::exp(0.2 * v_comp)), ((-(1)))) * ((-(0.6826183)) - 0.0091 * v_comp)), ((-(1))));
}

// AMPA_NMDA synapse end ///////////////////////////////////////////////////////////






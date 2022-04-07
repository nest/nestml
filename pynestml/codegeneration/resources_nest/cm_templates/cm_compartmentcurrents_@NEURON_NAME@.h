#ifndef SYNAPSES_NEAT_H_CMDEFAULTNESTML
#define SYNAPSES_NEAT_H_CMDEFAULTNESTML

#include <stdlib.h>

#include "ring_buffer.h"



namespace nest
{

class Na{
private:
// user-defined parameters Na channel (maximal conductance, reversal potential)
    // state variable m
    double m_Na = 0.0;
    // state variable h
    double h_Na = 0.0;
// state variables Na channel
    // parameter gbar
    double gbar_Na = 0.0;
    // parameter e
    double e_Na = 50.0;

public:
    // constructor, destructor
    Na();
    Na(const DictionaryDatum& channel_params);
    ~Na(){};

    // initialization channel
    void calibrate(){m_Na = 0.0;h_Na = 0.0;};
    void append_recordables(std::map< Name, double* >* recordables,
                            const long compartment_idx);

    // numerical integration step
    std::pair< double, double > f_numstep( const double v_comp );

    // function declarations

    //  functions Na
double m_inf_Na(double) const
;

    //
double tau_m_Na(double) const
;


    //
double h_inf_Na(double) const
;

    //
double tau_h_Na(double) const
;


};


class K{
private:
// user-defined parameters K channel (maximal conductance, reversal potential)
    // state variable n
    double n_K = 0.0;
// state variables K channel
    // parameter gbar
    double gbar_K = 0.0;
    // parameter e
    double e_K = (-(85.0));

public:
    // constructor, destructor
    K();
    K(const DictionaryDatum& channel_params);
    ~K(){};

    // initialization channel
    void calibrate(){n_K = 0.0;};
    void append_recordables(std::map< Name, double* >* recordables,
                            const long compartment_idx);

    // numerical integration step
    std::pair< double, double > f_numstep( const double v_comp );

    // function declarations

    //  functions K
double n_inf_K(double) const
;

    //
double tau_n_K(double) const
;


};
////////////////////////////////////////////////// synapses



class AMPA{
private:
  // global synapse index
  long syn_idx = 0;

  // propagators, initialized via calibrate() to 0, refreshed in numstep
  double __P__g_AMPA__X__spikes_AMPA__g_AMPA__X__spikes_AMPA;
  double __P__g_AMPA__X__spikes_AMPA__g_AMPA__X__spikes_AMPA__d;
  double __P__g_AMPA__X__spikes_AMPA__d__g_AMPA__X__spikes_AMPA;
  double __P__g_AMPA__X__spikes_AMPA__d__g_AMPA__X__spikes_AMPA__d;

  // kernel state variables, initialized via calibrate()
  double g_AMPA__X__spikes_AMPA;
  double g_AMPA__X__spikes_AMPA__d;

  // user defined parameters, initialized via calibrate()
  double tau_d_AMPA;
  double tau_r_AMPA;
  double e_AMPA;

  // user declared internals in order they were declared, initialized via calibrate()
  double tp_AMPA;
  double g_norm_AMPA;

  // spike buffer
  RingBuffer* spikes_AMPA_;

public:
  // constructor, destructor
  AMPA( const long syn_index);
  AMPA( const long syn_index, const DictionaryDatum& receptor_params);
  ~AMPA(){};

  // numerical integration step
  std::pair< double, double > f_numstep( const double v_comp, const long lag );

  // calibration
  void calibrate();
  void append_recordables(std::map< Name, double* >* recordables);
  void set_buffer_ptr( std::vector< RingBuffer >& syn_buffers )
  {
    spikes_AMPA_ = &syn_buffers[ syn_idx ];
  };

  // function declarations
  
  //  functions K
double n_inf_K(double) const
;
  
  //
double tau_n_K(double) const
;
  
  //  functions Na
double m_inf_Na(double) const
;
  
  //
double tau_m_Na(double) const
;
  
  //
double h_inf_Na(double) const
;
  
  //
double tau_h_Na(double) const
;
  
};




class GABA{
private:
  // global synapse index
  long syn_idx = 0;

  // propagators, initialized via calibrate() to 0, refreshed in numstep
  double __P__g_GABA__X__spikes_GABA__g_GABA__X__spikes_GABA;
  double __P__g_GABA__X__spikes_GABA__g_GABA__X__spikes_GABA__d;
  double __P__g_GABA__X__spikes_GABA__d__g_GABA__X__spikes_GABA;
  double __P__g_GABA__X__spikes_GABA__d__g_GABA__X__spikes_GABA__d;

  // kernel state variables, initialized via calibrate()
  double g_GABA__X__spikes_GABA;
  double g_GABA__X__spikes_GABA__d;

  // user defined parameters, initialized via calibrate()
  double tau_r_GABA;
  double tau_d_GABA;
  double e_GABA;

  // user declared internals in order they were declared, initialized via calibrate()
  double tp_GABA;
  double g_norm_GABA;

  // spike buffer
  RingBuffer* spikes_GABA_;

public:
  // constructor, destructor
  GABA( const long syn_index);
  GABA( const long syn_index, const DictionaryDatum& receptor_params);
  ~GABA(){};

  // numerical integration step
  std::pair< double, double > f_numstep( const double v_comp, const long lag );

  // calibration
  void calibrate();
  void append_recordables(std::map< Name, double* >* recordables);
  void set_buffer_ptr( std::vector< RingBuffer >& syn_buffers )
  {
    spikes_GABA_ = &syn_buffers[ syn_idx ];
  };

  // function declarations
  
  //  functions K
double n_inf_K(double) const
;
  
  //
double tau_n_K(double) const
;
  
  //  functions Na
double m_inf_Na(double) const
;
  
  //
double tau_m_Na(double) const
;
  
  //
double h_inf_Na(double) const
;
  
  //
double tau_h_Na(double) const
;
  
};




class NMDA{
private:
  // global synapse index
  long syn_idx = 0;

  // propagators, initialized via calibrate() to 0, refreshed in numstep
  double __P__g_NMDA__X__spikes_NMDA__g_NMDA__X__spikes_NMDA;
  double __P__g_NMDA__X__spikes_NMDA__g_NMDA__X__spikes_NMDA__d;
  double __P__g_NMDA__X__spikes_NMDA__d__g_NMDA__X__spikes_NMDA;
  double __P__g_NMDA__X__spikes_NMDA__d__g_NMDA__X__spikes_NMDA__d;

  // kernel state variables, initialized via calibrate()
  double g_NMDA__X__spikes_NMDA;
  double g_NMDA__X__spikes_NMDA__d;

  // user defined parameters, initialized via calibrate()
  double e_NMDA;
  double tau_d_NMDA;
  double tau_r_NMDA;

  // user declared internals in order they were declared, initialized via calibrate()
  double tp_NMDA;
  double g_norm_NMDA;

  // spike buffer
  RingBuffer* spikes_NMDA_;

public:
  // constructor, destructor
  NMDA( const long syn_index);
  NMDA( const long syn_index, const DictionaryDatum& receptor_params);
  ~NMDA(){};

  // numerical integration step
  std::pair< double, double > f_numstep( const double v_comp, const long lag );

  // calibration
  void calibrate();
  void append_recordables(std::map< Name, double* >* recordables);
  void set_buffer_ptr( std::vector< RingBuffer >& syn_buffers )
  {
    spikes_NMDA_ = &syn_buffers[ syn_idx ];
  };

  // function declarations
  
  //  functions K
double n_inf_K(double) const
;
  
  //
double tau_n_K(double) const
;
  
  //  functions Na
double m_inf_Na(double) const
;
  
  //
double tau_m_Na(double) const
;
  
  //
double h_inf_Na(double) const
;
  
  //
double tau_h_Na(double) const
;
  
};




class AMPA_NMDA{
private:
  // global synapse index
  long syn_idx = 0;

  // propagators, initialized via calibrate() to 0, refreshed in numstep
  double __P__g_AN_NMDA__X__spikes_AN__g_AN_NMDA__X__spikes_AN;
  double __P__g_AN_NMDA__X__spikes_AN__g_AN_NMDA__X__spikes_AN__d;
  double __P__g_AN_NMDA__X__spikes_AN__d__g_AN_NMDA__X__spikes_AN;
  double __P__g_AN_NMDA__X__spikes_AN__d__g_AN_NMDA__X__spikes_AN__d;
  double __P__g_AN_AMPA__X__spikes_AN__g_AN_AMPA__X__spikes_AN;
  double __P__g_AN_AMPA__X__spikes_AN__g_AN_AMPA__X__spikes_AN__d;
  double __P__g_AN_AMPA__X__spikes_AN__d__g_AN_AMPA__X__spikes_AN;
  double __P__g_AN_AMPA__X__spikes_AN__d__g_AN_AMPA__X__spikes_AN__d;

  // kernel state variables, initialized via calibrate()
  double g_AN_NMDA__X__spikes_AN;
  double g_AN_NMDA__X__spikes_AN__d;
  double g_AN_AMPA__X__spikes_AN;
  double g_AN_AMPA__X__spikes_AN__d;

  // user defined parameters, initialized via calibrate()
  double tau_d_AN_NMDA;
  double tau_r_AN_NMDA;
  double NMDA_ratio;
  double tau_r_AN_AMPA;
  double e_AN_AMPA;
  double tau_d_AN_AMPA;
  double e_AN_NMDA;

  // user declared internals in order they were declared, initialized via calibrate()
  double tp_AN_AMPA;
  double g_norm_AN_AMPA;
  double tp_AN_NMDA;
  double g_norm_AN_NMDA;

  // spike buffer
  RingBuffer* spikes_AN_;

public:
  // constructor, destructor
  AMPA_NMDA( const long syn_index);
  AMPA_NMDA( const long syn_index, const DictionaryDatum& receptor_params);
  ~AMPA_NMDA(){};

  // numerical integration step
  std::pair< double, double > f_numstep( const double v_comp, const long lag );

  // calibration
  void calibrate();
  void append_recordables(std::map< Name, double* >* recordables);
  void set_buffer_ptr( std::vector< RingBuffer >& syn_buffers )
  {
    spikes_AN_ = &syn_buffers[ syn_idx ];
  };

  // function declarations
  
  //  functions K
double n_inf_K(double) const
;
  
  //
double tau_n_K(double) const
;
  
  //  functions Na
double m_inf_Na(double) const
;
  
  //
double tau_m_Na(double) const
;
  
  //
double h_inf_Na(double) const
;
  
  //
double tau_h_Na(double) const
;
  
};


///////////////////////////////////////////// currents

class CompartmentCurrentsCmDefaultNestml {
private:
  // ion channels

  Na Na_chan_;
  
  K K_chan_;
  

  // synapses
  std::vector < AMPA > AMPA_syns_;
  
  std::vector < GABA > GABA_syns_;
  
  std::vector < NMDA > NMDA_syns_;
  
  std::vector < AMPA_NMDA > AMPA_NMDA_syns_;
  public:
  CompartmentCurrentsCmDefaultNestml(){};
  explicit CompartmentCurrentsCmDefaultNestml(const DictionaryDatum& channel_params)
  {
    Na_chan_ = Na( channel_params );
    
    K_chan_ = K( channel_params );
    };
  ~CompartmentCurrentsCmDefaultNestml(){};

  void calibrate(){
    // initialization of the ion channels
    Na_chan_.calibrate();
    
    K_chan_.calibrate();
    // initialization of synapses
    // initialization of AMPA synapses
    for( auto syn_it = AMPA_syns_.begin();
         syn_it != AMPA_syns_.end();
         ++syn_it )
    {
      syn_it->calibrate();
    }
  
    // initialization of GABA synapses
    for( auto syn_it = GABA_syns_.begin();
         syn_it != GABA_syns_.end();
         ++syn_it )
    {
      syn_it->calibrate();
    }
  
    // initialization of NMDA synapses
    for( auto syn_it = NMDA_syns_.begin();
         syn_it != NMDA_syns_.end();
         ++syn_it )
    {
      syn_it->calibrate();
    }
  
    // initialization of AMPA_NMDA synapses
    for( auto syn_it = AMPA_NMDA_syns_.begin();
         syn_it != AMPA_NMDA_syns_.end();
         ++syn_it )
    {
      syn_it->calibrate();
    }
  }

  void add_synapse( const std::string& type, const long syn_idx )
  {
     if ( type == "AMPA" )
    {
      AMPA_syns_.push_back( AMPA( syn_idx ) );
    }
  
    else if ( type == "GABA" )
    {
      GABA_syns_.push_back( GABA( syn_idx ) );
    }
  
    else if ( type == "NMDA" )
    {
      NMDA_syns_.push_back( NMDA( syn_idx ) );
    }
  
    else if ( type == "AMPA_NMDA" )
    {
      AMPA_NMDA_syns_.push_back( AMPA_NMDA( syn_idx ) );
    }
  else
    {
      assert( false );
    }
  };
  void add_synapse( const std::string& type, const long syn_idx, const DictionaryDatum& receptor_params )
  {
     if ( type == "AMPA" )
    {
      AMPA_syns_.push_back( AMPA( syn_idx, receptor_params ) );
    }
  
    else if ( type == "GABA" )
    {
      GABA_syns_.push_back( GABA( syn_idx, receptor_params ) );
    }
  
    else if ( type == "NMDA" )
    {
      NMDA_syns_.push_back( NMDA( syn_idx, receptor_params ) );
    }
  
    else if ( type == "AMPA_NMDA" )
    {
      AMPA_NMDA_syns_.push_back( AMPA_NMDA( syn_idx, receptor_params ) );
    }
  else
    {
      assert( false );
    }
  };

  void
  add_receptor_info( ArrayDatum& ad, const long compartment_index )
  {
    for( auto syn_it = AMPA_syns_.begin(); syn_it != AMPA_syns_.end(); syn_it++)
    {
      DictionaryDatum dd = DictionaryDatum( new Dictionary );
      def< long >( dd, names::receptor_idx, syn_it->get_syn_idx() );
      def< long >( dd, names::comp_idx, compartment_index );
      def< std::string >( dd, names::receptor_type, "AMPA" );
      ad.push_back( dd );
    }
    
    for( auto syn_it = GABA_syns_.begin(); syn_it != GABA_syns_.end(); syn_it++)
    {
      DictionaryDatum dd = DictionaryDatum( new Dictionary );
      def< long >( dd, names::receptor_idx, syn_it->get_syn_idx() );
      def< long >( dd, names::comp_idx, compartment_index );
      def< std::string >( dd, names::receptor_type, "GABA" );
      ad.push_back( dd );
    }
    
    for( auto syn_it = NMDA_syns_.begin(); syn_it != NMDA_syns_.end(); syn_it++)
    {
      DictionaryDatum dd = DictionaryDatum( new Dictionary );
      def< long >( dd, names::receptor_idx, syn_it->get_syn_idx() );
      def< long >( dd, names::comp_idx, compartment_index );
      def< std::string >( dd, names::receptor_type, "NMDA" );
      ad.push_back( dd );
    }
    
    for( auto syn_it = AMPA_NMDA_syns_.begin(); syn_it != AMPA_NMDA_syns_.end(); syn_it++)
    {
      DictionaryDatum dd = DictionaryDatum( new Dictionary );
      def< long >( dd, names::receptor_idx, syn_it->get_syn_idx() );
      def< long >( dd, names::comp_idx, compartment_index );
      def< std::string >( dd, names::receptor_type, "AMPA_NMDA" );
      ad.push_back( dd );
    }
    void
  set_syn_buffers( std::vector< RingBuffer >& syn_buffers )
  {
    // spike buffers for synapses
    for( auto syn_it = AMPA_syns_.begin(); syn_it != AMPA_syns_.end(); syn_it++)
      syn_it->set_buffer_ptr( syn_buffers );
    
    for( auto syn_it = GABA_syns_.begin(); syn_it != GABA_syns_.end(); syn_it++)
      syn_it->set_buffer_ptr( syn_buffers );
    
    for( auto syn_it = NMDA_syns_.begin(); syn_it != NMDA_syns_.end(); syn_it++)
      syn_it->set_buffer_ptr( syn_buffers );
    
    for( auto syn_it = AMPA_NMDA_syns_.begin(); syn_it != AMPA_NMDA_syns_.end(); syn_it++)
      syn_it->set_buffer_ptr( syn_buffers );
    };

  std::map< Name, double* >
  get_recordables( const long compartment_idx )
  {
    std::map< Name, double* > recordables;

    // append ion channel state variables to recordables
    Na_chan_.append_recordables( &recordables, compartment_idx );
    
    K_chan_.append_recordables( &recordables, compartment_idx );
    // append synapse state variables to recordables
    for( auto syn_it = AMPA_syns_.begin(); syn_it != AMPA_syns_.end(); syn_it++)
      syn_it->append_recordables( &recordables );
    
    for( auto syn_it = GABA_syns_.begin(); syn_it != GABA_syns_.end(); syn_it++)
      syn_it->append_recordables( &recordables );
    
    for( auto syn_it = NMDA_syns_.begin(); syn_it != NMDA_syns_.end(); syn_it++)
      syn_it->append_recordables( &recordables );
    
    for( auto syn_it = AMPA_NMDA_syns_.begin(); syn_it != AMPA_NMDA_syns_.end(); syn_it++)
      syn_it->append_recordables( &recordables );
    return recordables;
  };

  std::pair< double, double >
  f_numstep( const double v_comp, const long lag )
  {
    std::pair< double, double > gi(0., 0.);
    double g_val = 0.;
    double i_val = 0.;
    // contribution of Na channel
    gi = Na_chan_.f_numstep( v_comp );

    g_val += gi.first;
    i_val += gi.second;

    
    // contribution of K channel
    gi = K_chan_.f_numstep( v_comp );

    g_val += gi.first;
    i_val += gi.second;

    
    // contribution of AMPA synapses
    for( auto syn_it = AMPA_syns_.begin();
         syn_it != AMPA_syns_.end();
         ++syn_it )
    {
      gi = syn_it->f_numstep( v_comp, lag );

      g_val += gi.first;
      i_val += gi.second;
    }
  
    // contribution of GABA synapses
    for( auto syn_it = GABA_syns_.begin();
         syn_it != GABA_syns_.end();
         ++syn_it )
    {
      gi = syn_it->f_numstep( v_comp, lag );

      g_val += gi.first;
      i_val += gi.second;
    }
  
    // contribution of NMDA synapses
    for( auto syn_it = NMDA_syns_.begin();
         syn_it != NMDA_syns_.end();
         ++syn_it )
    {
      gi = syn_it->f_numstep( v_comp, lag );

      g_val += gi.first;
      i_val += gi.second;
    }
  
    // contribution of AMPA_NMDA synapses
    for( auto syn_it = AMPA_NMDA_syns_.begin();
         syn_it != AMPA_NMDA_syns_.end();
         ++syn_it )
    {
      gi = syn_it->f_numstep( v_comp, lag );

      g_val += gi.first;
      i_val += gi.second;
    }
  return std::make_pair(g_val, i_val);
  };

};

} // namespace

#endif /* #ifndef SYNAPSES_NEAT_H_CMDEFAULTNESTML */
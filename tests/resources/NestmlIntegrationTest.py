
import nest
import pylab

nest.Install("models")
nest.set_verbosity("M_WARNING")

def test(referenceModel, testant, gsl_error_tol, tolerance = 0.000001):
  nest.ResetKernel()
  neuron1=nest.Create (referenceModel)
  neuron2=nest.Create (testant)

  if not (gsl_error_tol is None):
    nest.SetStatus(neuron2, {"gsl_error_tol": gsl_error_tol})

  spikegenerator=nest.Create('spike_generator',params={'spike_times':[100.0, 200.0], 'spike_weights':[1.0, -1.0]})

  nest.Connect(spikegenerator, neuron1)
  nest.Connect(spikegenerator, neuron2)

  multimeter1=nest.Create('multimeter')
  multimeter2=nest.Create('multimeter')

  V_m_specifier = 'V_m'# 'delta_V_m'
  nest.SetStatus (multimeter1, {"withtime":True, "record_from":[V_m_specifier]})
  nest.SetStatus (multimeter2, {"withtime":True, "record_from":[V_m_specifier]})

  nest.Connect (multimeter1, neuron1)
  nest.Connect (multimeter2, neuron2)

  nest.Simulate (400.0)
  dmm1=nest.GetStatus(multimeter1)[0]
  Vms1=dmm1["events"][V_m_specifier]
  ts1=dmm1["events"]["times"]

  events1=dmm1["events"]
  pylab.figure(1)

  dmm2=nest.GetStatus(multimeter2)[0]
  Vms2=dmm2["events"][V_m_specifier]
  ts2=dmm2["events"]["times"]

  #pylab.plot(ts1, Vms1, label = "Reference " + referenceModel)
  #pylab.plot(ts2, Vms2, label = "Testant " + testant)
  #pylab.legend(loc='upper right')

  for index in range(0, len(Vms1)):
  	if abs(Vms1[index]-Vms2[index]) > tolerance:
  		print('!!!!!!!!!!!!!!!!!!!!')
  		print(str(Vms1[index]) + " divers from  " + str(Vms2[index]) + " at iteration: " + str(index) + " of overall iterations: " + str(len(Vms1)))
  		print('!!!!!!!!!!!!!!!!!!!!')
  		raise Exception(testant + ": TEST FAILED")
  	elif abs(Vms1[index]-Vms2[index]) > 0:
  		None #print("Greater than 0 difference" + str(abs(Vms1[index]-Vms2[index])) + " at iteration: " + str(index) + " of overall iterations: " + str(len(Vms1)))
  print(testant + " PASSED")


def test_multysinapse():
  neuron1=nest.Create ("iaf_psc_alpha_multisynapse_neuron")
  neuron2=nest.Create ("iaf_psc_alpha_multisynapse_neuron")

  nest.SetDefaults("iaf_psc_alpha_multisynapse", {"tau_syn": [1.0,2.0]})


  spikegenerator=nest.Create('spike_generator',params={'spike_times':[100.0, 200.0] })

  syn_dict ={"model": "static_synapse", "weight":2.5, 'receptor_type': 1}

  nest.Connect(spikegenerator, neuron2, syn_spec= syn_dict)
  nest.Connect(spikegenerator, neuron1, syn_spec= syn_dict)

  #nest.SetStatus(neuron1, {"I_e": 376.0})
  #nest.SetStatus(neuron2, {"I_e": 376.0})

  multimeter1=nest.Create('multimeter')
  multimeter2=nest.Create('multimeter')

  V_m_specifier = 'V_m'# 'delta_V_m'
  nest.SetStatus (multimeter1, {"withtime":True, "record_from":[V_m_specifier]})
  nest.SetStatus (multimeter2, {"withtime":True, "record_from":[V_m_specifier]})

  nest.Connect (multimeter1, neuron1)
  nest.Connect (multimeter2, neuron2)

  nest.Simulate (400.0)
  dmm1=nest.GetStatus(multimeter1)[0]
  Vms1=dmm1["events"][V_m_specifier]
  ts1=dmm1["events"]["times"]

  events1=dmm1["events"]
  pylab.figure(1)

  dmm2=nest.GetStatus(multimeter2)[0]
  Vms2=dmm2["events"][V_m_specifier]
  ts2=dmm2["events"]["times"]

  pylab.plot(ts1,Vms1)
  pylab.plot(ts2,Vms2)

  pylab.show()

  for index in range(0, len(Vms1)):
    if abs(Vms1[index]-Vms2[index]) > 0.000001:
      print('!!!!!!!!!!!!!!!!!!!!')
      print(str(Vms1[index]) + " divers from  " + str(Vms2[index]) + " at iteration: " + str(index) + " of overall iterations: " + str(len(Vms1)))
      print('!!!!!!!!!!!!!!!!!!!!')
      raise Exception("TEST FAILED")
    elif abs(Vms1[index]-Vms2[index]) > 0:
      print("Greater than 0 difference" + str(abs(Vms1[index]-Vms2[index])) + " at iteration: " + str(index) + " of overall iterations: " + str(len(Vms1)))
  print("Test: PASSED")




if __name__ == "__main__":
  # execute only if run as a script
  # test_multysinapse()
  models = list()
  
  models.append( ("aeif_cond_alpha", "aeif_cond_alpha_implicit", 1.e-3, 0.001))
  models.append( ("aeif_cond_exp", "aeif_cond_exp_implicit", 1.e-3, 0.001))
  models.append( ("hh_cond_exp_traub", "hh_cond_exp_traub_implicit", 1.e-3, 0.001))
  models.append( ("hh_psc_alpha", "hh_psc_alpha_implicit", 1.e-3, 0.001))
  models.append( ("iaf_chxk_2008", "iaf_chxk_2008_implicit", 1.e-3, 0.001))
  models.append( ("iaf_cond_alpha", "iaf_cond_alpha_implicit", 1.e-3, 0.001))
  models.append( ("iaf_cond_beta_neuron", "iaf_cond_beta_neuron", None, 0.001))
  models.append( ("iaf_cond_exp", "iaf_cond_exp_implicit", 1.e-3, 0.001))
  models.append( ("iaf_cond_exp_sfa_rr", "iaf_cond_exp_sfa_rr_implicit", 1.e-3, 0.001))
  models.append( ("iaf_neuron", "iaf_neuron_nestml", None, 0.001))
  models.append( ("iaf_psc_alpha", "iaf_psc_alpha_neuron", None, 0.001))
  models.append( ("iaf_psc_delta", "iaf_psc_delta", None, 0.001))
  models.append( ("iaf_psc_exp", "iaf_psc_exp_neuron", None, 0.01))    
  models.append( ("iaf_tum_2000", "iaf_tum_2000_neuron", None, 0.01))
  models.append( ("izhikevich", "izhikevich_neuron", 1.e-3, 0.5))
  models.append( ("izhikevich_psc_alpha", "izhikevich_psc_alpha_implicit", 1.e-3, 0.01))
  models.append( ("mat2_psc_exp", "mat2_psc_exp_neuron", None, 0.1))
  models.append( ("terub_neuron_gpe", "terub_neuron_gpe_implicit", 1.e-3, 0.001))
  models.append( ("terub_neuron_stn", "terub_neuron_stn_implicit", 1.e-3, 0.001))


  for reference, testant, gsl_error_tol, tollerance in models:
    test(reference, testant, gsl_error_tol, tollerance)

  

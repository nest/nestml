
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

  spikegenerator=nest.Create('spike_generator',params={'spike_times':[100.0, 200.0], 'spike_weights':[20.0, -20.0]})

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

  pylab.plot(ts1, Vms1, label = "Reference " + referenceModel)
  pylab.plot(ts2, Vms2, label = "Testant " + testant)
  pylab.legend(loc='upper right')

  pylab.show()
  for index in range(0, len(Vms1)):
  	if abs(Vms1[index]-Vms2[index]) > tolerance:
  		print('!!!!!!!!!!!!!!!!!!!!')
  		print(str(Vms1[index]) + " divers from  " + str(Vms2[index]) + " at iteration: " + str(index) + " of overall iterations: " + str(len(Vms1)))
  		print('!!!!!!!!!!!!!!!!!!!!')
  		raise Exception(testant + ": TEST FAILED")
  	elif abs(Vms1[index]-Vms2[index]) > 0:
  		None #print("Greater than 0 difference" + str(abs(Vms1[index]-Vms2[index])) + " at iteration: " + str(index) + " of overall iterations: " + str(len(Vms1)))
  print(testant + " PASSED")

if __name__ == "__main__":
  # execute only if run as a script
  # test_multysinapse()
  models = list()

  models.append( ("terub_neuron_stn", "terub_neuron_stn_implicit", 1.e-3, 0.001))
  # models.append( ("iaf_cond_exp_sfa_rr", "iaf_cond_exp_sfa_rr_implicit", None, 0.001))

  for reference, testant, gsl_error_tol, tollerance in models:
    test(reference, testant, gsl_error_tol, tollerance)


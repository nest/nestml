import copy
import numpy as np
import nest

def strip_suffix(l, suffix):
	new_l = []
	for n in l:
		if n[-len(suffix):] == suffix:
			n = n[:-len(suffix)]
		new_l.append(n)
	return new_l


models = nest.Models(mtype="nodes")
neuron_models = [m for m in models if str(nest.GetDefaults(m, "element_type")) == "neuron"]
_neuron_models = strip_suffix(neuron_models, "_neuron")
syn_models = nest.Models(mtype="synapses")


print("Before: had " + str(len(neuron_models)) + " neuron models")





#import os
#os.environ["NEST_PATH"] = "/home/archels/julich/nest-simulator-build"
#os.environ["LD_LIBRARY_PATH"] = "/home/archels/julich/nest-simulator-build/lib:/home/archels/julich/nest-simulator-build/lib/python3.6/site-packages/nest:/tmp/nestml-target"
#os.environ["SLI_PATH"] = "/tmp/nestml-target/sli"

from pynestml.frontend.pynestml_frontend import to_nest, install_nest

#to_nest(input_path="/home/archels/julich/nestml-fork/nestml/models/aeif_cond_alpha.nestml", target_path="/tmp/nestml-target", suffix="_nestml", logging_level="INFO")
#to_nest(input_path="/home/archels/julich/nestml-fork/nestml/models/ht_neuron.nestml", target_path="/tmp/nestml-target", suffix="_nestml")
to_nest(input_path="/home/archels/julich/nestml-fork/nestml/models", target_path="/tmp/nestml-target", suffix="_nestml")

install_nest("/tmp/nestml-target", "/home/archels/julich/nest-simulator-build")

nest.set_verbosity("M_ALL")
#nest.set_debug(True)

nest.Install("nestmlmodule")

#nest.Simulate(1.)





new_models = nest.Models(mtype="nodes")
new_neuron_models = [m for m in new_models if str(nest.GetDefaults(m, "element_type")) == "neuron"]
_new_neuron_models = strip_suffix(new_neuron_models, "_nestml")
_new_neuron_models = strip_suffix(_new_neuron_models, "_neuron")
new_syn_models = nest.Models(mtype="synapses")

print("After: have " + str(len(new_neuron_models)) + " neuron models")

all_models = np.sort(list(set(_neuron_models) | set(_new_neuron_models)))

fname = "/tmp/models_coverage.html"
html_file = open(fname, "w")
html_file.write("""
<meta charset="UTF-8">
<html>
<head>
<style>
td { padding: 3px; font-weight: bold }
.header td { background-color:#ddeeff; padding: 5px !important }
.check_yes {background-color: #00ff33 }
.check_no {background-color: #dd3300 }
tr { margin-bottom: 5px; margin-top: 5px }
tr:nth-child(even) { background: #eee }
tr:nth-child(odd) { background: #fff }
</style>
</head>
<body>
""")
html_file.write("<table>")
html_file.write("\t<tr class=\"header\"><td>Model name</td><td>NEST?</td><td>NESTML?</td><td>Behavioural</td></tr>")

for i, n in enumerate(all_models):
	html_file.write("\t<tr>")

	html_file.write("\t<td>" + n + "</td>")

	if n in neuron_models or n + "_neuron" in neuron_models:
		html_file.write("\t<td class=\"check_yes\">✓</td>")
	else:
		html_file.write("\t<td class=\"check_no\">✗</td>")

	if n + "_nestml" in new_neuron_models or n + "_neuron_nestml" in new_neuron_models:
		html_file.write("\t<td class=\"check_yes\">✓</td>")
	else:
		html_file.write("\t<td class=\"check_no\">✗</td>")

	html_file.write("\t<td>?</td>")

	html_file.write("\t</tr>")

html_file.write("</table>")

html_file.write(str(len(all_models)) + " models total")
html_file.write("</body></html>")

html_file.close()

print("Wrote " + fname)

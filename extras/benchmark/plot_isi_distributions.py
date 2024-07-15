import os
import numpy as np
import matplotlib.pyplot as plt


def read_isis_from_files(neuron_models):
    data = {}
    for neuron_model in neuron_models:
        data[neuron_model] = {"isis": []}
        iteration = 0
        rank = 0
        while True:
            filename = "isi_distribution_[simulated_neuron=" + neuron_model + "]_[network_scale=20000]_[iteration=" + str(iteration) + "]_[nodes=2]_[rank=" + str(rank) + "]_isi_list.txt"
            if not os.path.exists(filename):
                break

            with open(filename, 'r') as file:
                isis = [float(line.strip()) for line in file]
                data[neuron_model]["isis"].append(isis)

            #iteration += 1
            rank += 1

    return data


def analyze_data(data, bin_size):
    # Determine the range for the bins
    min_val = np.inf
    max_val = -np.inf
    for neuron_model in data.keys():
        isi_list = data[neuron_model]["isis"]
        for isi in isi_list:
            min_val = min(min_val, min(isi))
            max_val = max(max_val, max(isi))

    bins = np.arange(min_val, max_val + bin_size, bin_size)

    for neuron_model in data.keys():
        isi_list = data[neuron_model]["isis"]
        data[neuron_model]["counts"] = len(isi_list) * [None]
        for i, isi in enumerate(isi_list):
            counts, bin_edges = np.histogram(isi, bins=bins)
            data[neuron_model]["counts"][i] = counts

        data[neuron_model]["counts_mean"] = np.mean(np.array(data[neuron_model]["counts"]), axis=0)
        data[neuron_model]["counts_std"] = np.std(np.array(data[neuron_model]["counts"]), axis=0)

    data["bin_centers"] = (bin_edges[:-1] + bin_edges[1:]) / 2
    data["min_val"] = min_val
    data["max_val"] = max_val

def plot_isi_distributions(neuron_models, data):
    plt.figure(figsize=(10, 6))

    for neuron_model in neuron_models:
        plt.step(data["bin_centers"], data[neuron_model]["counts_mean"], label=neuron_model, linewidth=2, alpha=.5)
        plt.errorbar(data["bin_centers"], data[neuron_model]["counts_mean"], yerr=data[neuron_model]["counts_std"], fmt='o', color='black', capsize=5, label='Variance')

    plt.xlabel('ISI (ms)')
    plt.ylabel('Frequency')
    plt.title('ISI Distributions')
    plt.legend()
    plt.grid(True)
    plt.show()

# Example usage
neuron_models = ["aeif_psc_alpha_neuron_Nestml_Plastic_noco__with_stdp_synapse_Nestml_Plastic_noco", "aeif_psc_alpha_neuron_Nestml_Plastic__with_stdp_synapse_Nestml_Plastic", "aeif_psc_alpha_neuron_Nestml", "aeif_psc_alpha"]

bin_size = 5  # Adjust the bin size as needed

data = read_isis_from_files(neuron_models)
analyze_data(data, bin_size)
plot_isi_distributions(neuron_models, data)


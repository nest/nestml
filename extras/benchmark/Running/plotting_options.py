import matplotlib.pyplot as plt

# Plotting options
palette = plt.get_cmap("Set1")

plt.rcParams['axes.grid'] = True

plt.rcParams['grid.color'] = 'gray'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.linewidth'] = 0.5

plt.rcParams['axes.labelsize'] = 16  # Size of the axis labels
plt.rcParams['xtick.labelsize'] = 14  # Size of the x-axis tick labels
plt.rcParams['ytick.labelsize'] = 14  # Size of the y-axis tick labels
plt.rcParams['legend.fontsize'] = 14  # Size of the legend labels
plt.rcParams['figure.titlesize'] = 16  # Size of the figure title

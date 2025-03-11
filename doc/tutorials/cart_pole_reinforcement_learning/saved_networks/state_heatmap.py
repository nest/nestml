import json
import matplotlib.pyplot as plt
import numpy as np

with open("network.json", "r") as f:
    network = json.load(f)

avg_weights_left = np.zeros((3,6,3,3))
avg_weights_right = np.zeros((3,6,3,3))
for s in network:
    state = eval(s) #converts string tuple back to string
    avg_weights_left[state[0], state[1], state[2], state[3]] = np.average(network[s]["connection_left"]["weight"])
    avg_weights_left[state[0], state[1], state[2], state[3]] = np.average(network[s]["connection_right"]["weight"])

avg_weights = avg_weights_right - avg_weights_left
plt.title("Weight for a state of (Position/Angle)")
# dimensions are (position, angle, velocity, angular velocity) indexed from 1
# axis=(2,3) plots angle and position and averages over the two selected ones
plt.imshow(np.mean(avg_weights, axis = (2,3)), cmap=plt.cm.coolwarm, vmin=-1, vmax=1, interpolation='none')
plt.ylabel("Position")
plt.xlabel("Angle")
plt.colorbar()
plt.show()
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0,5,100)
y = 24*x

plt.axhline(y = 2, color = 'r', linestyle = '-')
plt.plot(x, y, '-r', label='y=2x+1')

plt.plot(0.672, 0.64, "ro")

ax = plt.gca()

ax.set_ylim([0, 3])
ax.set_xlim([0, 1])



plt.show()
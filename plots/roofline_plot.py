import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0,5,100)
y = 22.27*x

plt.axhline(y = 4, color = 'r', linestyle = '-')
plt.plot(x, y, '-r', label='y=2x+1')

plt.plot(8., 16/508, "ro")
plt.plot(8., 16/634, "ro")
plt.plot(8., 16/1249, "ro")

ax = plt.gca()

ax.set_ylim([0, 6])
ax.set_xlim([-0.2, 12])



plt.show()
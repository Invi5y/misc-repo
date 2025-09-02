import numpy as np
from matplotlib.patches import Polygon
import matplotlib as mlp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D



strike = np.linspace(50,150,24)
ttm = np.linspace(0.5,2.5,24)
strike, ttm = np.meshgrid(strike, ttm)
# print(strike,"\n\n\n\n",ttm)

iv = (strike - 100) ** 2 / (100 * strike) / ttm
# print(ttm.shape)

fig = plt.figure(figsize=(10,6))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(strike, ttm, iv)
plt.show()

print('hello')

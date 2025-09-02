import numpy as np
from matplotlib.patches import Polygon
import matplotlib as mlp
import matplotlib.pyplot as plt

def func(x):
    return 0.5 * np.exp(x) + 1

a,b = 0.5, 1.5

x = np.linspace(0, 2)
y = func(x)
Ix = np.linspace(a, b)
Iy = func(Ix)
verts = [(a,0)] + list(zip(Ix, Iy)) + [(b,0)]
# print(type(x),y, Ix, Iy,verts)

fig, ax = plt.subplots(figsize=(10,6))
plt.plot(x,y,'b',linewidth=2)
plt.ylim(bottom=0)
poly = Polygon(verts,facecolor='0.7')
ax.add_patch(poly)
plt.text(0.5 * (a+b), 1, r'$\int_a^b f(x)\mathrm{d}x$', 
         horizontalalignment='center', fontsize=20)

plt.show()

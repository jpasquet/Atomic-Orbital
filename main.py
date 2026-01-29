import math
import random
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


a0 = 5.29e-11

def densite_1s(r):
    return (1 / (math.pi * a0**3)) * math.exp(-1 * r / a0)

def generate_points_1s(N=20000, r_max=5*a0):
    points = []
    rho_max = densite_1s(0)
    while len(points) < N:
        x = random.uniform(-r_max, r_max)
        y = random.uniform(-r_max, r_max)
        z = random.uniform(-r_max, r_max)

        r = math.sqrt(x*x + y*y + z*z)
        if r > r_max:
            continue

        if random.random() < densite_1s(r) / rho_max:
            points.append((x, y, z))

    return np.array(points)

points = generate_points_1s()

r = np.sqrt(points[:,0]**2 + points[:,1]**2 + points[:,2]**2)

fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, projection='3d')

sc = ax.scatter(
    points[:,0], points[:,1], points[:,2],
    c=r,
    cmap='plasma',
    s=1,
    alpha=0.4
)

ax.set_title("Orbitale 1s – densité colorée par r")
ax.set_box_aspect([1,1,1])
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.set_zlabel("z (m)")

plt.colorbar(sc, label="Distance au noyau (m)")
plt.show()
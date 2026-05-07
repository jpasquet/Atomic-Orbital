import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np



a0 = 5.29*10**-11
r_max = 5 * a0    


 

def Probap(N, Z, a0, type="2pz"):
    x = np.random.normal(0, a0, N)
    y = np.random.normal(0, a0, N)
    z = np.random.normal(0, a0, N)

    r = np.sqrt(x**2 + y**2 + z**2)

    theta= np.arccos(np.where(r == 0, 0, z / r))
    phi=np.arctan2(y,x)
    cos_theta = np.where(r == 0, 0, z / r)
     
    if(type=="1s"):
        constante = 1/np.sqrt(np.pi)*(Z/a0)**(3.0/2.0)
        psi = constante * np.exp(-Z*r/a0)
    elif(type=="2s"):
        constante = 1/np.sqrt(32*np.pi) * (Z/a0)**(3.0/2.0)
        psi = constante * np.exp(-Z*r/(2*a0)) * (2 - Z*r/a0)
    elif(type=="3s"):
        constante = 1/np.sqrt(4*np.pi)* 2/(81*np.sqrt(3))  * (Z/a0)**(3.0/2.0)
        psi = constante * np.exp(-Z*r/(3*a0)) * (27 - 18*Z*r/a0 + 2*(Z*r/a0)**2)
    elif(type=="2pz"):
        constante = 1/np.sqrt(32*np.pi) * (Z/a0)**(5.0/2.0)
        psi = constante * np.exp(-Z*r/(2*a0)) * r * cos_theta
    elif(type=="2px"):
        constante = 1/np.sqrt(32*np.pi)
        psi = constante * np.exp(-Z*r/(2*a0)) * r * np.sin(theta) * np.cos(phi)
    elif(type=="2py"):
        constante = 1/np.sqrt(32*np.pi)
        psi = constante * np.exp(-Z*r/(2*a0)) * r * np.sin(theta) * np.sin(phi)
    else:
        raise ValueError("Type d'orbitale non reconnu. Utilisez '1s', '2s', '3s', '2pz', '2px' ou '2py'.")

    proba = psi**2
    filtre = r!=-10
    return x[filtre],y[filtre],z[filtre]   ,proba[filtre], psi[filtre]


liste = ["1s", "2s", "2pz", "2px", "2py"]

for name in liste:
    X, Y, Z, proba,psi= Probap(100000, Z=1, a0=a0, type=name)

    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, projection='3d')
    threshold = proba.max() * 0.0
    pos = (psi > 0) & (proba > threshold)
    neg = (psi < 0) & (proba > threshold)

    ax.scatter(X[pos]/a0, Y[pos]/a0, Z[pos]/a0, c='red', s=6, alpha=0.6, label='psi > 0')
    ax.scatter(X[neg]/a0, Y[neg]/a0, Z[neg]/a0, c='blue', s=6, alpha=0.6, label='psi < 0')

    ax.set_xlabel('x / a0')
    ax.set_ylabel('y / a0')
    ax.set_zlabel('z / a0')
    ax.set_title('Orbital '+name+' — 3D')
    ax.legend()

    ax.set_box_aspect((1,1,1))

    plt.show()


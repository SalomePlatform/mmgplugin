import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import linregress
from scipy.signal import savgol_filter
import random
from loggerpy.loggingMld import *

logger = Logger()
logger.set_level("info")

should_save = False
logger.info("Document saving : " + str(should_save))

def classic_plot(X, Y, xlabel="x", ylabel="y", title=""):
    """plot the 1 parameter study graph"""
    plt.figure(figsize=(10, 8))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    a,b,r,p,err=linregress(X,Y) # régression linéaire
    def modele(x,a,b):
        return a*x+b

    # Apply the Savitzky-Golay filter for smoothing
    window_length = 11  # Adjust the window length as needed
    polyorder = 2       # Adjust the polynomial order as needed
    y_smooth = savgol_filter(Y, window_length, polyorder)

    plt.plot(X, Y, ls=" ", marker="o", ms=5, mew=2, label="Data", color='grey')
    plt.plot(X,modele(X,a,b), label="Model", color='blue')
    plt.plot(X, y_smooth, label='Smoothed Curve', color='red')

    plt.figlegend([title])
    plt.grid()
    if should_save:
        plt.savefig('../studies/classic/' + title.split('\n')[0] + '_' + xlabel + '_' + ylabel + '.png')
    plt.show()

def plot(X, Y, c_vect, xlabel="x", ylabel="y", barlabel="bar", title=""):
    """plot the 2 parameter study graph"""
    plt.figure(figsize=(10, 8))
    cmap = plt.get_cmap('viridis')
    scatter = plt.scatter(X, Y, c=c_vect, cmap=cmap, s=100)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    scatter.set_clim(vmin=0)
    cmap.set_under('white')
    plt.colorbar(scatter, label=barlabel)
    plt.figlegend([title])
    if should_save:
        plt.savefig('../studies/' + title.split('\n')[0] + '_' + xlabel + '_' + ylabel + '_' + barlabel + '.png')
    plt.show()

def plot3D(X, Y, Z, c_vect, xlabel="x", ylabel="y", zlabel="z", barlabel="bar", title=""):
    """plot the 3 parameter study graph"""
    X_grid, Y_grid, Z_grid = np.meshgrid(X, Y, Z, indexing='ij')

    X_flat = X_grid.flatten()
    Y_flat = Y_grid.flatten()
    Z_flat = Z_grid.flatten()


    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    cmap = plt.get_cmap('viridis')
    scatter = ax.scatter3D(X_flat, Y_flat, Z_flat, c=c_vect.flatten() ,cmap=cmap, marker='o', s=100)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)

    scatter.set_clim(vmin=0)
    cmap.set_under('white')
    fig.colorbar(scatter, ax=ax, label=barlabel)
    ax.set_title(title)
    if should_save:
        plt.savefig('../studies/3D/' + title.split('\n')[0] + str(random.randint(1, 10000)) + '.png')
    plt.show()

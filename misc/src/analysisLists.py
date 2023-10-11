import numpy as np
from listsLogs import *
from matplotlib import pyplot as plt
from loggerpy.loggingMld import *

logger = Logger()
logger.set_level("info")

should_save = True
logger.info("Document saving : " + str(should_save))

def plot_hist(X, title=""):
    """plot the 1 parameter study graph"""
    plt.figure(figsize=(10, 8))
    plt.xlabel('aspect ratio')
    plt.ylabel('number of faces')

    plt.hist(X, bins=100, edgecolor='black')

    plt.figlegend([title])
    plt.grid()
    if should_save:
        plt.savefig('../studies/histograms/' + title + '.png')
    plt.show()

def wrap_print(text='', indent_level=0):
    print(indent_level*"  " + text)

def print_info(value, name):
    wrap_print(name + ":")
    wrap_print("Max: " + str(max(value)), 1)
    wrap_print("Avg: " + str(sum(value) / len(value)), 1)
    wrap_print("Ecart-type: " + str(np.std(value)), 1)
    wrap_print('-------')

AllLists = ['HeadAspects', 'HumanAspects', 'ConeAspects', 'ThinkerAspects', \
        'NewThinkerAspects', 'PipeAspects', 'SphereAspects']
for name in AllLists:
    value = globals()[name]
    print_info(value, name)
    plot_hist(value, name)

import numpy as np

from matplotlib import pyplot as plt, axes

from pyrecorder.recorder import Recorder
from pyrecorder.writers.gif import GIF

from sympy import sympify, Expr
from sympy.abc import x,y,z,w
from coreplotlib import create_plot

import json

import os
            
def create_mix_plot():    
    vars:np.ndarray = np.load(os.getcwd()+'\\..\\static\\temp\\raw_vars.npy')
    vals:np.ndarray = np.load(os.getcwd()+'\\..\\static\\temp\\raw_vals.npy')
    with open(os.getcwd()+'\\..\\static\\temp\\data.json') as JSON:
        data:dict = json.load(JSON)

    for i, f in enumerate(data['f']):
        data['f'][i] = sympify(f)
    
    grid = (2,2)
    poss = ((0,0), (0,1), (1,0), (1,1))
    
    fig, axs = plt.subplots(*grid)    
    
    for i, pos in enumerate(poss):
        axs[*pos].remove()
        if 0 <= i < len(data['f']):            
            custom_ax = create_plot(
                fig = fig,
                plot_pos = [*grid, i+1],
                f = data['f'][i],
                name =  data['names'][i],
                limits = data['limits'],
            )
            
            symbols = get_symbols(data['f'][i])
            
            variables = []
            for elem in symbols:
                variables.append(vars[0][elem])
            
            custom_ax.scatter(*variables, vals[0][i], marker='x', color='red')
            
    
    fig.tight_layout()
    
def get_symbols(f:Expr):
    symbols = []
             
    # reading symbols
    if f.has(x) and not(x in symbols):
        symbols.append(0)
    if f.has(y) and not(y in symbols):
        symbols.append(1)
    if f.has(z) and not(z in symbols):
        symbols.append(2)
    if f.has(w) and not(w in symbols):
        symbols.append(3)
        
    return symbols

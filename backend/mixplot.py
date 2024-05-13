import numpy as np

from matplotlib import pyplot as plt, animation, axes

from sympy import sympify, Expr
from sympy.abc import x,y,z,w
from coreplotlib import create_plot

import json

import os
            
def create_mix_plot():
    vars:np.ndarray = np.load(os.path.dirname(os.path.abspath(__file__))+'\\..\\static\\temp\\raw_vars.npy')
    vals:np.ndarray = np.load(os.path.dirname(os.path.abspath(__file__))+'\\..\\static\\temp\\raw_vals.npy')
    with open(os.path.dirname(os.path.abspath(__file__))+'\\..\\static\\temp\\data.json') as JSON:
        data:dict = json.load(JSON)

    for i, f in enumerate(data['f']):
        data['f'][i] = sympify(f)
    
    grid = (2,2)
    poss = ((0,0), (0,1), (1,0), (1,1))
    
    fig, axs = plt.subplots(*grid)    
    
    
    new_axs:list[axes.Axes] = []
    scaters = []
    
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
            
            new_axs.append(custom_ax)
    
    
    def update(frame):
        fig.suptitle(f'Iteración {frame}/{vals.shape[0]}')
        for i, pos in enumerate(poss):
            if 0 <= i < len(data['f']):       
                symbols = get_symbols(data['f'][i])
                
                variables = []
                for elem in symbols:
                    variables.append(vars[frame][elem])
                
                if len(scaters) < len(new_axs):
                    scaters.append(new_axs[i].scatter(*variables, vals[frame][i], marker='x', color='red'))
                else:
                    if len(variables) == 1:
                        a = np.stack(list(zip(*variables, vals[frame][i])))
                        scaters[i].set_offsets(a)
                    elif len(variables) == 2:
                        scaters[i]._offsets3d = (*variables, vals[frame][i])
                
                
        return fig, *scaters
                
    ani = animation.FuncAnimation(fig=fig, func=update, frames = vars.shape[0], interval=30)
    ani.save('./../static/rendered_plots/animacion.gif', dpi=200, fps=6)
    
    fig.tight_layout()
    
    plt.show()
    
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

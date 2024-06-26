import os
import numpy as np
from matplotlib import pyplot as plt, axes, figure
from sympy import Expr
from sympy.abc import x, y, z, w

def eval_f(f:Expr, variables, values) -> float:
    """Evalúa un objeto Exp de sympify para devolver el resultado"""
    return f.subs(dict(zip(variables, values))).evalf()

def create_plot(fig:figure.Figure, plot_pos:list, f:Expr, name:str, limits:list, density:int = 50) -> figure.Figure:
    
    """Crea un objeto Figure a partir de una expresión matemática\
        de sympify y unos límites deternimados.\
        Retorna el objeto fig para visualizarlo, guardarlo como imagen,\
        añadir más plots al mismo, etc."""
    
    symbols = []
    
    # reading symbols
    if f.has(x) and not(x in symbols):
        symbols.append(x)
    if f.has(y) and not(y in symbols):
        symbols.append(y)
    if f.has(z) and not(z in symbols):
        symbols.append(z)
    if f.has(w) and not(w in symbols):
        symbols.append(w)
    
    # 2D function
    if len(symbols) == 1:
        if not str(symbols[0]) in limits:
            return "faltan"
        
        print([*limits[str(symbols[0])], density])
        X = np.linspace(*limits[str(symbols[0])], density)
        Y = [eval_f(f, symbols, [x]) for x in X]
        
        ax = fig.add_subplot(*plot_pos)
        
        return custom_plot_2d(
            ax = ax,
            x = X,
            y = Y,
            title = name,
            variable = symbols[0]
            )
    

    # 3D function                
    if len(symbols) == 2:
        if not str(symbols[0]) in limits or not str(symbols[1]) in limits:
            return "faltan"
        
        X = np.linspace(*limits[str(symbols[0])], density)
        Y = np.linspace(*limits[str(symbols[1])], density)
        X, Y = np.meshgrid(X, Y)
        Z = np.empty_like(X)
        
        for i in range(X.shape[0]):
            for j in range(Y.shape[1]):
                Z[i, j] = eval_f(
                    f = f,
                    variables = symbols,
                    values = [X[i, j], Y[i, j]]
                )
        
        ax = fig.add_subplot(*plot_pos, projection = "3d")
        
        return custom_plot_3d(
            ax = ax,
            x = X,
            y = Y,
            z = Z,
            title = name,
            variables = symbols
        )
    

def custom_plot_2d(ax:axes.Axes, x, y, title:str, variable) -> axes.Axes:
    """Caso donde requiere crear un plot de una curva"""
    ax.plot(x, y)
    ax.grid()
    ax.set_title(title)
    ax.set_xlabel("Eje " + str(variable))
    ax.set_ylabel(f'f({str(variable)})')
    
    return ax
        
        
def custom_plot_3d(ax:axes.Axes, x, y, z, title:str, variables:list) -> axes.Axes:
    """Caso donde requiere crear un plot de una superficie"""
    ax.plot_surface(x, y, z,
                    cmap = 'viridis',
                    edgecolor = 'none')
    ax.grid()
    ax.set_title(title)
    ax.set_xlabel("Eje " + str(variables[0]))
    ax.set_ylabel("Eje " + str(variables[1]))
    
    return ax
    
    
    
def create_historic_view(fig:figure.Figure, history:dict, generations:int) -> figure.Figure:
    progress = [h['best_score'] for h in history]
    ax = fig.add_subplot()
    ax.plot(list(range(generations)), progress)
    ax.grid()
    ax.set_title("Evolución del mejor resultado")
    return fig
    
    
def save_plot_at_location(figure:figure.Figure, filename:str, dpi):
    figure.savefig(os.path.dirname(os.path.abspath(__file__))+f'\\..\\static\\rendered_plots\\{filename}.png', dpi=dpi)
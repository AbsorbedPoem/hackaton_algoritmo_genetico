import numpy as np
from matplotlib import pyplot as plt, axes, figure
from sympy import Expr
from sympy.abc import x, y, z, w

def eval_f(f:Expr, variables, values) -> float:
    """Evalúa un objeto Exp de sympify para devolver el resultado"""
    return f.subs(dict(zip(variables, values))).evalf()

def create_plot(f:Expr, name:str, limits:list, density:int = 50) -> figure.Figure:
    
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
        X = np.linspace(*limits, density)
        Y = [eval_f(f, symbols, [x]) for x in X]
        
        fig, ax = plt.subplots()
        
        custom_plot_2d(
            ax = ax,
            x = X,
            y = Y,
            title = name,
            variable = symbols[0]
            )

    # 3D function                
    if len(symbols) == 2:
        X = np.linspace(*limits, density)
        Y = np.linspace(*limits, density)
        X, Y = np.meshgrid(X, Y)
        Z = np.empty_like(X)
        
        for i in range(X.shape[0]):
            for j in range(Y.shape[1]):
                Z[i, j] = eval_f(
                    f = f,
                    variables = symbols,
                    values = [X[i, j], Y[i, j]]
                )
                
        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        
        custom_plot_3d(
            ax = ax,
            x = X,
            y = Y,
            z = Z,
            title = name,
            variables = symbols
        )
    
    return fig
    

def custom_plot_2d(ax:axes.Axes, x, y, title:str, variable):
    """Caso donde requiere crear un plot de una curva"""
    ax.plot(x, y)
    ax.grid()
    ax.set_title(title)
    ax.set_xlabel("Eje " + str(variable))
    ax.set_ylabel(f'f({str(variable)})')
        
        
def custom_plot_3d(ax:axes.Axes, x, y, z, title:str, variables:list) -> axes.Axes:
    """Caso donde requiere crear un plot de una superficie"""
    ax.plot_surface(x, y, z,
                    cmap = 'viridis',
                    edgecolor = 'none')
    ax.grid()
    ax.set_title(title)
    ax.set_xlabel("Eje " + str(variables[0]))
    ax.set_ylabel("Eje " + str(variables[1]))
    
    
def save_plot_at_location(figure:figure.Figure, filename:str, dpi):
    figure.savefig(f'./../static/rendered_plots/{filename}.png', dpi=dpi)
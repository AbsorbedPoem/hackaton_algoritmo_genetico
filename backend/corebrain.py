import os
import numpy as np

import sympy
from sympy import sympify, lambdify
from sympy.abc import x, y, z, w

from matplotlib import use
use('agg')
from matplotlib import pyplot as plt
from coreplotlib import create_plot, create_historic_view, save_plot_at_location

import json

class genAlgorithm :
    
    def __init__(self, n_indivs:int = 100, n_generations:int = 5, mutation_rate:float = .05, limits:list[float | int] = [-5, 5]):
        
        self.n_indivs:int = n_indivs
        self.n_generations:int = n_generations
        self.mutation_rate:float = mutation_rate
        
        self.limits:list[float] = limits
        
        self.gen_pool:dict = {
            "integer" : list(range(limits[0]+1, limits[1])),
            "decimal" : list(range(-9, 10))
        }
        
        self.variables:list = list()
        self.functions:list[sympy.Expr] = []
        self.functions_names:list[str] = []
        self.priorities:list[float] = []
        
        self.population:list = []
        
        self.metrics:list = dict()
        self.history:list = []
        self.best_result:list = {
            'interation' : None,
            'best_score' : -99999999,
            'best_result' : []
        }
        
        self.np_variables:np.ndarray = None
        self.np_values:np.ndarray = None
        
        
    #######################################################
    # CREACION Y GESTION DE FUNCIONES
    #######################################################
    
    
    def is_valid_function(self) -> bool:
        """Verifica si una funciond es validad para sympify"""
        try:
            f = sympify(function)
            return True
        except ValueError:
            return False
    
    def append_function(self, function:str, name:str = '', priority:float = 1) -> bool:
        """Añade una función objetivo, sobre las cuales se evaluará la suma ponderada"""
        try:
            f = sympify(function)
            self.functions.append(f)
            if (name == ''):
                self.functions_names.append(f'Funcion {len(self.functions)}')
            else:
                self.functions_names.append(name)
            self.priorities.append(priority)
            self.check_variables()
            return True
        except ValueError:
            raise Exception("formato inválido para funcion, intenta corregir signos de puntuación, o ser mas explícito")
        
        
    def eval_f(self, index:int, args:dict) -> float:
        """Evalúa la funcion objetivo del índice i (lista de funciones), y retorna el resultado"""
        return self.functions[index].evalf(subs=args)
    
    
    def check_variables(self) -> None:
        
        """Varifica la existencia de las variables x, y, z o w\
        dentro de las funciones existentes, y les añade la prioridad 1\
        por defecto para la suma ponderada"""
        
        for f in self.functions:
            if f.has(x) and not(x in self.variables):
                self.variables.append(x)
            if f.has(y) and not(y in self.variables):
                self.variables.append(y)
            if f.has(z) and not(z in self.variables):
                self.variables.append(z)
            if f.has(w) and not(w in self.variables):
                self.variables.append(w)

    
    
    #######################################################
    # GERACION DE INDIVIDUOS Y POBLACION
    #######################################################
    
    
    def create_indiv(self) -> list[int]:
        """Genera un nuevo individuo"""
        indiv = []
        
        for _ in self.variables:
            indiv.append(
                [
                    np.random.choice(self.gen_pool["integer"])
                ] +\
                list(np.random.choice(
                    self.gen_pool["decimal"],
                    14
                ))
            )
        return indiv
    
    
    def create_population(self) -> None:
        """Crea una nueva poblacion mediante la generacion una serie de nuevos individuos"""
        if(len(self.variables) != 0 ):
            for _ in range(self.n_indivs):
                self.population.append(self.create_indiv())
        else :
            raise Exception("No se han definido variables independientes para el problema")
            
            
    
    #######################################################
    # CRUZAMIENTO Y MUTACION
    #######################################################
        
    
    def prepare_inputs(self, iteration:int) -> None:
        for i, indiv in enumerate(self.population):
            for v, val in enumerate(indiv):
                self.np_variables[iteration, v, i] = decode_2_float(val)
    
    
    def get_per_f_scores(self, iteration:int) -> None:
        for i, expr in enumerate(self.functions):
            f = lambdify([self.variables], expr, "numpy")
            
            
            
            self.np_values[iteration, i] = f(self.np_variables[iteration])
            
    def get_scores(self, scores:np.ndarray):
        for i in range(scores.shape[0]):
            scores[i] = scores[i] * self.priorities[i]
        
        return scores.sum(axis = 0)
    
    
    def binary_fision(self, indiv:list) -> list:
        """Fisiona individuos padres, para generar un nuevo hijo a partir de sus fragmentos"""
        descendent = []
        for i in range(len(indiv[0])):
            fis_point = np.random.randint(self.n_indivs)
            descendent.append(indiv[0][i][:fis_point] + indiv[1][i][fis_point:])
        return descendent
    
    
    def mutate_indiv(self, indiv:list) -> list:
        """ Toma un conjunto de individuos y cambia algunos de sus genes en base a un factor de probabilidad """
        for i in range(len(indiv)):
            for j in range(len(indiv[0])):
                if np.random.random() < self.mutation_rate:
                    mutated_gen = np.random.choice(self.gen_pool["decimal" if j > 0 else "integer"])
                    indiv[i] = indiv[i][0:j] + [mutated_gen] + indiv[i][j + 1:]
        return indiv


    
    #######################################################
    # MAIN LOOP
    #######################################################
    
    
    def run(self, verbose:bool = False) -> None:
        """ Función gatillo del Main Loop. El argumento verbose\
            indica si se quieren o no imprimir los resultados de las iteraciones. \
            El argumento display_plots decide si generar o no un gráfico de histórico mas un gif de avance"""
            
        self.np_variables = np.zeros((self.n_generations, len(self.variables), self.n_indivs), dtype='float64')
        self.np_values = np.zeros((self.n_generations, len(self.functions), self.n_indivs), dtype='float64')
        
        self.create_population()
            
        # vuelta principal
        for i in range(self.n_generations):
            self.next_gen(
                iteration = i,
                verbose = verbose,
                display_plots = True
            )
            
        # variables json para la generacion del gif
        self.update_gif_data()
            
        # Creación del gráfico histórico
        fig = create_historic_view(plt.figure(), self.history, self.n_generations)
        save_plot_at_location(fig, 'historico', 100)
        
        # Guardadndo en archivos binarios
        np.save(os.path.dirname(os.path.abspath(__file__))+'\\..\\static\\temp\\raw_vars', self.np_variables)
        np.save(os.path.dirname(os.path.abspath(__file__))+'\\..\\static\\temp\\raw_vals', self.np_values)
    
    
    def next_gen(self, iteration:int, verbose = True, display_plots = True) -> None:
        """main loop del avance de una generación"""
        new_population = []
        
        # preparacion de los geneses en floats, en un numpy array
        self.prepare_inputs(iteration = iteration)
        # calculo de la funcion sobre los arrays
        self.get_per_f_scores(iteration = iteration)
        # suma de los puntajes de la funciones para obtener el fitness
        scores = self.get_scores(self.np_values[iteration])
        
        
        # control de metricas
        self.update_metrics(iteration, scores, verbose)
            
        # los pesos deben estar normalizados para usar el algoritmo de selección
        scores -= np.amin(scores)
        if scores.sum() == 0.0:
            return
        scores /= scores.sum()
        
        
        for _ in self.population:
            # se seleccionan los padres en base a la distribucion de probabilidad dada por lo pesos
            parents = list(np.random.choice(len(self.population), size = 2, p = scores))
            # efectuacion de la particion binara y la mutacion para cada par de padres seleccionado
            new_indiv = self.binary_fision([self.population[parents[0]], self.population[parents[1]]])
            new_indiv = self.mutate_indiv(new_indiv)
            # se añade el nuevo individuo
            new_population.append(new_indiv)
        
        self.population = new_population
        
        
    def update_metrics(self, iter:int, scores:list[float], verbose = True, display_plots = True) -> list:
        """ Genear un diccionario de metricas para la población existente, a modo de registro """
        metrics = dict()
        
        metrics['iteration'] = iter + 1
        metrics['best_score'] = np.amax(scores)
        
        best_element_index = np.where(scores == metrics['best_score'])[0][0]
        best_element = self.population[best_element_index]
        
        metrics['best_result'] = dict()
        
        for v, var in enumerate(best_element):
            metrics['best_result'][str(self.variables[v])] = decode_2_float(var)
            
        # añadiendo el score al historial
        self.history.append(metrics)
        
        # actualizando el mejor puntaje si es que existe
        if metrics['best_score'] > self.best_result['best_score']:
            self.best_result = metrics
            
        if verbose:
            print(metrics)
            
            
    def update_gif_data(self) -> None:
        data = dict()
        data['names'] = self.functions_names
        data['limits'] = self.limits
        data['f'] = []
        
        for i, f in enumerate(self.functions):
            data['f'].append(str(f))
        
        with open(os.path.dirname(os.path.abspath(__file__))+'\\..\\static\\temp\\data.json', 'w') as fp:
            json.dump(data, fp)
            
        

def decode_2_float(num:list) -> float:
    """Decodifica los 15 genes de un individuo en un número flotante"""
    decimal = 0
    j = 0
    if num[0] > 0:
        for i in range( len(num)):
            decimal += num[i]*10**(-i)
        return decimal
    else:
        for i in range(len(num)-1): 
            j-= 1
            decimal+= num[i+1]*10**(j)
            r = decimal + (-1*num[0])
            r = -1*r
    return r


def is_valid_function(f:str, nombre:str, limites:list[float]):
    
    # Debug
    limites = [0, 4]
    
    try:
        # Verificacion de la funcion
        f:sympy.Expr = sympify(f)
        has = []
        
        deny_pool = [
            "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "v",
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "V", "W", "X", "Y", "Z"
        ]
        accept_pool = [
            'x', 'y', 'z', 'w'
        ]
        
        for symbol in deny_pool:
            if f.has(sympy.symbols(symbol)):
                raise ValueError('')
        for symbol in accept_pool:
            if f.has(sympy.symbols(symbol)):
                has.append(symbol)
                
        if len(has) == 0:
            raise ValueError('')
        
        # Creacion del plot de la funcion
        fig = plt.figure()
        
        create_plot(
            fig = fig,
            plot_pos = [1, 1, 1],
            f = f,
            name = nombre,
            limits = limites,
            density = 100
        )
        
        save_plot_at_location(figure = fig, filename = nombre, dpi = 200)
        
        return f"<b>{f}</b> tiene: "+json.dumps(has)
    
    except ValueError:
        return False

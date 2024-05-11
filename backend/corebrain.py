import numpy as np
from mpl_toolkits.mplot3d.axes3d import get_test_data

from pyrecorder.recorder import Recorder
from pyrecorder.writers.gif import GIF

import sympy
from sympy import sympify
from sympy.abc import x, y, z, w

from matplotlib import pyplot as plt
from coreplotlib import create_plot

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
    
    def append_function(self, function:str, priority:float = 1) -> bool:
        """Añade una función objetivo, sobre las cuales se evaluará la suma ponderada"""
        try:
            f = sympify(function)
            self.functions.append(f)
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
    
    
    def get_score(self, indiv:list, indiv_index:int, iteration:int) -> float:
        
        """ Revisa un individuo y obtiene el puntaje, ademas de almacenas los\
        resultados en las variables np_variables y np_values para la posterior\
        generación de gráficos """
        
        score = 0
        vars = dict.fromkeys(self.variables, True)
    
        for i, var in enumerate(vars):
            vars[var] = decode_2_float(indiv[i])
            self.np_variables[iteration, indiv_index, i] = vars[var]
            
        for i in range(len(self.functions)):
            s = self.eval_f(index = i, args = vars) * self.priorities[i]
            self.np_values[iteration, indiv_index, i] = s
            score += s
        
        return score
    
    
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
            
        self.np_variables = np.zeros((self.n_generations, self.n_indivs, len(self.variables)), dtype='float64')
        self.np_values = np.zeros((self.n_generations, self.n_indivs, len(self.functions)), dtype='float64')
            
        # vuelta principal
        for i in range(self.n_generations):
            self.next_gen(
                iteration = i,
                verbose = verbose,
                display_plots = True
            )
            if verbose:
                print(i)
                
        # Generación del gráfico de histórico
        
        # Guardadndo en archivos binarios
        np.save(f'./../static/temp/raw_vars.png', self.np_variables)
        np.save(f'./../static/temp/raw_vals.png', self.np_values)
    
    
    def next_gen(self, iteration:int, verbose = True, display_plots = True) -> None:
        """main loop del avance de una generación"""
        new_population = []
        scrs = []
        
        # los scores son el valor "fitness" de cada individuo,
        # por lo que se almacenan para hacer una selección ponderada
        for i, indiv in enumerate(self.population):
            scrs.append(self.get_score(
                indiv = indiv,
                indiv_index = i,
                iteration = iteration
                )
            )
        
        # control de metricas
        scores:np.ndarray = np.array(scrs, dtype='float64')
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
            
            
    #######################################################
    # VISUALIZATION
    #######################################################
            
            
    # def display_plots(self):
        
    #     grid = (2,2)
    #     poss = ((0,0), (0,1), (1,0), (1,1))
        
    #     fig, axs = plt.subplots(*grid)
        
    #     for i, pos in enumerate(poss):
    #         axs[*pos].remove()
    #         if 0 <= i < len(self.functions):
    #             custom_ax = create_plot(
    #             fig = fig,
    #             plot_pos = [*grid, i+1],
    #             f = self.functions[i],
    #             name = f'Función {i+1}',
    #             limits = self.limits,
    #     )
        
    #     fig.tight_layout()
    
        

def decode_2_float(num) -> float:
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

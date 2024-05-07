import numpy as np
import sympy
import matplotlib.pyplot as plt
from pyrecorder.recorder import Recorder
from pyrecorder.writers.gif import GIF
from sympy import sympify
from sympy.abc import x, y, z, w

class genAlgorithm :
    
    def __init__(self, n_indivs = 100, n_generations = 15, mutation_rate = .15, limits = [-5,5]):
        
        self.n_indivs:int = n_indivs
        self.n_generations:int = n_generations
        self.mutation_rate:float = mutation_rate
        
        self.gen_pool:dict = {
            "integer" : list(range(limits[0]+1, limits[1])),
            "decimal" : list(range(-9, 10))
        }
        
        self.variables:list = list()
        self.functions:list[sympy.Expr] = []
        self.priorities:list[float] = []
        self.population:list = []
        
        
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
        
        
    def eval_f(self, index:int, values:list[float | int]) -> float:
        """Evalúa la funcion objetivo del índice i (lista de funciones), y retorna el resultado"""
        return self.functions[index].subs(dict(zip(self.variables, values))).evalf()
    
    
    def check_variables(self) -> None:
        
        """Varifica la existencia de las variables x, y, z o w\
        dentro de las funciones existentes, y les añade la prioridad 1\
        por defecto para la suma ponderada"""
        
        for f in self.functions:            
            if f.has(x) and not('x' in self.variables):
                self.variables.append('x')
            if f.has(y) and not('y' in self.variables):
                self.variables.append('y')
            if f.has(z) and not('z' in self.variables):
                self.variables.append('z')
            if f.has(w) and not('w' in self.variables):
                self.variables.append('w')

    
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
    
    
    def get_score(self, indiv:list) -> float:
        score = 0
        args = []
        for row in indiv:
            args.append(decode_2_float(row))
        
        for i in range(len(self.functions)):
            score += self.eval_f(index = i, values = args) * self.priorities[i]
        return score
    
    
    def binary_fision(self, indiv:list) -> list:
        """Fisiona individuos padres, para generar un nuevo hijo a partir de sus fragmentos"""
        descendent = []
        for i in range(len(indiv[0])):
            print(i)
            fis_point = np.random.randint(self.n_indivs)
            descendent.append(indiv[0][i][:fis_point] + indiv[1][i][fis_point:])
        return descendent
    
    
    def mutate_indiv(self, indiv:list) -> list:
        """Toma un conjunto de individuos"""
        for i in range(len(indiv)):
            for j in range(len(indiv[0])):
                if np.random.random() < self.mutation_rate:
                    mutated_gen = np.random.choice(self.gen_pool["decimal" if j > 0 else "integer"])
                    indiv[i] = indiv[i][0:j] + [mutated_gen] + indiv[i][j + 1:]
        return indiv

    
    #######################################################
    # VISUALIZACION
    #######################################################
    
    
    
    
    
    #######################################################
    # MAIN LOOP
    #######################################################
    
    
    def next_gen(self) -> None:
        """main loop del avance de una generación"""
        new_population = []
        scrs = []
        
        # los scores son el valor "fitness" de cada individuo,
        # por lo que se almacenan para hacer una selección ponderada
        for indiv in self.population:
            scrs.append(self.get_score(indiv = indiv))
            
        scores:np.ndarray = np.array(scrs, dtype='float64')
            
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
    
    
    #######################################################
    # MATPLOT
    #######################################################





def decode_2_float(num) -> float:
    """Decodifica los 15 genes de un individuo en un número flotante"""
    decimal = 0
    j = 0
    if num[0] > 0:
        for i in range(len(num)):
            decimal+= num[i]*10**(-i)
        return decimal  
    else:
        for i in range(len(num)-1): 
            j-= 1
            decimal+= num[i+1]*10**(j)
            r = decimal + (-1*num[0])
            r = -1*r
    return r
        


gen_system = genAlgorithm(
    n_indivs = 6
)

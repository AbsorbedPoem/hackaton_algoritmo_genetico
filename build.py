import sys
sys.path.append('backend')

from flask import Flask, render_template, request
from flaskwebgui import FlaskUI

from backend import corebrain, mixplot, coreplotlib
from matplotlib import pyplot as plt

import json

app = Flask(__name__)

ui = FlaskUI(
    app = app,
    server = 'flask',
    width = 500,
    height = 500
)

@app.route('/')
def inicio():
	return render_template('index.html')

@app.route('/resultados/', methods=['GET'])
def mostrar_resultados():
    """ Llamada para generar el resultado del algoritmo, y así poder dar un valor concreto """
    data = request.args.get('data')
    
    data = json.loads("""
    {
        "n_individuos" : 500,
        "n_generaciones" : 50,
        "ratio_mutacion" : 0.0005,
        "funcs" : [
            "38*x + 5",
            "cos(x)*500 + y**3 + 20*x",
            "0.8*((-y)+3)**3 + 4.33"
        ],
        "limites" : [
            [0, 10],
            [0, 20],
        ],
        "nombres" : [
            "funciona 1",
            "funciona 2",
            "funciona 3"
        ],
        "prioridades" : [
            1,
            1,
            1
        ]
    }
    """)
    
    n_inividuos = data['n_individuos']
    n_generaciones = data['n_generaciones']
    ratio_mutacion = data['ratio_mutacion']
    limites = data['limites']
    
    funciones = data['funcs']
    nombres = data['nombres']
    prioridades = data['prioridades']
    
    gen_system = corebrain.genAlgorithm(
        n_indivs = n_inividuos,
        n_generations = n_generaciones,
        mutation_rate = ratio_mutacion,
        limits = limites
    )
    
    for i in range(len(funciones)):
        gen_system.append_function(
            function = funciones[i],
            name = nombres[i],
            priority = prioridades[i]
        )
        
    gen_system.run(verbose = False)
    
    mejor_resultado = gen_system.best_result
    
    return json.dumps(mejor_resultado)
 
@app.route('/es_funcion_valida/', methods=['POST'])
def es_valida():
    """ Llamada para verificar si una funcion tipeada en el input es válida y tiene las variables necesitadas """
    data = json.loads(request.form.get('data'))
    
    # funcion:str = fr"{repr(data['funcion'])}"
    funcion:str = data['funcion']
    # funcion = r"x^2 + \frac{4}{5}"
    # funcion = funcion.replace('\\', '\\')
    
    nombre = data['nombre']
    limites = data['limites']
    
    result = dict()
    result = corebrain.is_valid_function(funcion, nombre, limites)
    
    if result == "faltan":
        return "faltan"
    elif result != False:
        return json.dumps({"tiene" : result, "url" : f"/static/rendered_plots/{nombre}.png"})
    else:
        return "fail"

    
@app.route('/generar_gif/', methods=['GET'])
def generar_gif():
    """ Una vez generados los resultados del algoritmo, se genera un GIF para el problema planteado """
    mixplot.create_mix_plot()
    return "done"
        

if __name__ == '__main__':
	app.run()

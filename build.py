from flask import Flask, render_template, request
from flaskwebgui import FlaskUI
from backend import corebrain, mixplot, coreplotlib
from matplotlib import pyplot as plt

app = Flask(__name__)

ui = FlaskUI(app=app, server='flask', width=500, height=500)

@app.route('/')
def inicio():
	return render_template('index.html')

@app.route('/resultados/', methods=['GET'])
def mostrar_resultados():
    """ Llamada para generar el resultado del algoritmo, y así poder dar un valor concreto """
    data = request.args.get('data')
    
    n_inividuos = data['n_individuos']
    n_generaciones = data['n_generaciones']
    ratio_mutacion = data['ratio_mutacion']
    
    funciones = data['funcs']
    nombres = data['nombres']
    prioridades = data['prioridades']
    limites = data['limites']
    
    gen_system = corebrain.genAlgorithm(
        n_indivs = n_inividuos,
        n_generations = n_generaciones,
        mutation_rate = ratio_mutacion,
        limits = limites
    )
    
    for i in len(range(funciones)):
        gen_system.append_function(
            function = funciones[i],
            name = nombres[i],
            priority = prioridades[i]
        )
        
    gen_system.run(verbose = False)
    
    return "done"
 
@app.route('/es_funcion_valida/', methods=['GET'])
def es_valida():
    """ Llamada para verificar si una funcion tipeada en el input es válida y tiene las variables necesitadas """
    funcion = request.args.get('funcion')
    nombre = request.args.get('nombre')
    
    result = corebrain.is_valid_function(funcion, nombre)
    if result != False:
        return result
    else:
        return "fail"

    
@app.route('/generar_gif/', methods=['GET'])
def generar_gif():
    """ Una vez generados los resultados del algoritmo, se genera un GIF para el problema planteado """
    mixplot.create_mix_plot()
    return "done"
        

if __name__ == '__main__':
	app.run()

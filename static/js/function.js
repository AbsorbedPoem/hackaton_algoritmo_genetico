

// function highlightVariables() {
//     var variables = ['x', 'y', 'z', 'w'];
//     var equations = [
//         document.getElementById('ecuacion1').value,
//         document.getElementById('ecuacion2').value,
//         document.getElementById('ecuacion3').value,
//         document.getElementById('ecuacion4').value,
//     ];

//     for (var i = 0; i < variables.length; i++) {
//         var element = document.getElementById(variables[i]);
//         if (equations.some(equation => equation.includes(variables[i]))) {
//             element.classList.add('highlight');
//         } else {
//             element.classList.remove('highlight');
//         }
//     }

// }

document.addEventListener('DOMContentLoaded', function(){
    var cajas_de_funciones = [
        document.querySelector('#f1'),
        document.querySelector('#f2'),
        document.querySelector('#f3'),
        document.querySelector('#f4')
    ]

    cajas_de_limites = [
        document.querySelector('#var-x'),
        document.querySelector('#var-y'),
        document.querySelector('#var-z'),
        document.querySelector('#var-w')
    ]

    cajas_de_funciones.forEach(caja => {
        let campo_de_funcion = caja.querySelector(".funcion");
        let campo_latex = caja.querySelector(".latex");
        let preview_latex = caja.querySelector(".latex-preview");
        
        let MQ = MathQuill.getInterface(2); // for backcompat
        let mathField = MQ.MathField(campo_de_funcion, {
            spaceBehavesLikeTab: true, // configurable
            handlers: {
                edit: function() { // useful event handlers
                    preview_latex.textContent = mathField.latex(); // simple API
                    campo_latex.value = mathField.latex(); // simple API
                }
            }
        });
    });

    var mathFieldSpan = document.getElementById('abc');
    var latexSpan = document.getElementById('latex');
    
    var MQ = MathQuill.getInterface(2); // for backcompat
    var mathField = MQ.MathField(mathFieldSpan, {
        spaceBehavesLikeTab: true, // configurable
        handlers: {
        edit: function() { // useful event handlers
            latexSpan.textContent = mathField.latex(); // simple API
        }
        }
    });

    window.verificar = (index) => {
        caja = cajas_de_funciones[index]
        data = {}

        tiene_variables = caja.querySelector('.tiene-variables')
        imagen = caja.querySelector('.thumbnail')

        data.funcion = caja.querySelector('.latex').value
        data.nombre = caja.querySelector('.nombre').value

        data.limites = {}
        cajas_de_limites.forEach(elem => {
            if(elem.querySelector('.available').checked) {
                data.limites[elem.querySelector('.var').value] = [
                    parseInt(elem.querySelector('.sup').value),
                    parseInt(elem.querySelector('.inf').value)
                ]
            }
        });

        if (data.funcion == ""){
            alert('Función vacía')
            return
        }
        if (data.nombre == ""){
            alert('nombre vacío')
            return
        }

        $.ajax({
            url : "/es_funcion_valida/",
            type: "POST",
            data : {data: JSON.stringify(data)}
        })
        .done(function(response){
            if (response == "fail"){
                alert("la funcion es inválida")
                imagen.setAttribute("src", "/static/img/default.png")
            }
            else if (response == "faltan"){
                alert("declara los límites de las variables")
                imagen.setAttribute("src", "/static/img/default.png")
            }
            else {
                response = JSON.parse(response)

                tiene_variables.value = response.tiene
                imagen.setAttribute("src", "")
                imagen.setAttribute("src", response.url)
            }
        })
    }

    cajas_de_limites.forEach(elem => {
        elem.querySelector('.available').addEventListener('change', function(e) {
            let checked = e.target.checked;
            if (checked){
                elem.querySelector('.sup').removeAttribute('disabled')
                elem.querySelector('.inf').removeAttribute('disabled')
            }
            else {
                elem.querySelector('.sup').setAttribute("disabled", "")
                elem.querySelector('.sup').value = ""
                elem.querySelector('.inf').setAttribute("disabled", "")
                elem.querySelector('.inf').value = ""
            }
        })
    });

    document.querySelector('#generar-resultado').addEventListener('click', function(event){
        event.preventDefault()

        data = {}

        data.n_individuos = parseInt(document.querySelector('#tamanoPoblacion').value)
        data.n_generaciones = parseInt(document.querySelector('#numeroIteraciones').value)
        data.ratio_mutacion = parseInt(document.querySelector('#ratioMutacion').value)
        
        data.funcs = []
        data.nombres = []
        data.prioridades = []
        data.limites = new Object()

        cajas_de_funciones.forEach(caja => {
            if (caja.querySelector('.tiene-variables').value != ""){
                data.funcs.push(caja.querySelector('.latex').value)
                data.nombres.push(caja.querySelector('.nombre').value)
                if (caja.querySelector(".max:checked") != null){
                    data.prioridades.push(1)
                }
                else if (caja.querySelector(".min:checked") != null) {
                    data.prioridades.push(-1)
                }
            }
        })

        cajas_de_limites.forEach(elem => {
            if (elem.querySelector('.available').checked){
                data.limites[elem.querySelector('.var').value] = [parseInt(elem.querySelector('.inf').value), parseInt(elem.querySelector('.sup').value)]
            }
        });

        console.log(data.funcs)
        if (data.funcs.length == 0){
            alert("No se han ingresado o validado funciones")
            return
        }

        if (Object.keys(data.limites).length == 0){
            alert("No se han establecido límites de variables")
            return
        }

        nombres_str = ""
        vars_str = ""

        data.nombres.forEach(elem => {
            nombres_str += `${elem},`
        });
        Object.keys(data.limites).forEach(elem => {
            vars_str += `${elem},`
        });

        iziToast.question({
            timeout: 20000,
            close: false,
            overlay: true,
            displayMode: 'once',
            id: 'question',
            zindex: 999,
            title: 'Hey',
            message: `Se usarán las funciones: [${nombres_str}] y las variables [${vars_str}], estás de acuerdo?`,
            position: 'center',
            buttons: [
                ['<button><b>Calcular</b></button>', function (instance, toast) {
                    document.querySelector("#data-form").value = JSON.stringify(data)
                    console.log(document.querySelector("#formulario-envio"))
                    document.querySelector("#formulario-envio").submit()
                }, true],
                ['<button>Cancelar</button>', function (instance, toast) {
                    instance.hide({ transitionOut: 'fadeOut' }, toast, 'button');
                }],
            ],
        });
    })
})
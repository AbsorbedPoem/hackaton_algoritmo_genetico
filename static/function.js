function highlightVariables() {
    var variables = ['x', 'y', 'z', 'w'];
    var equations = [
        document.getElementById('ecuacion1').value,
        document.getElementById('ecuacion2').value,
        document.getElementById('ecuacion3').value,
        document.getElementById('ecuacion4').value,
        
    ];
    for (var i = 0; i < variables.length; i++) {
        var element = document.getElementById(variables[i]);
        if (equations.some(equation => equation.includes(variables[i]))) {
            element.classList.add('highlight');
        } else {
            element.classList.remove('highlight');
        }
    }

}

// var answerSpan = document.getElementById('abc');
// var answerMathField = MQ.MathField(answerSpan, {
//   handlers: {
//     edit: function() {
//       var enteredMath = answerMathField.latex(); // Get entered math in LaTeX format
//       checkAnswer(enteredMath);
//     }
//   }
// });

document.addEventListener('DOMContentLoaded', function(){
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
})
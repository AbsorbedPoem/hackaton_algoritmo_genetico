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
  
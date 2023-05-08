class DrawingState {
    constructor(x, y, angle) {
        this.x = x;
        this.y = y;
        this.angle = angle
    }
}

function generateSVGPaths(result, translations) {
    translations = parseTranslations(translations)
    let path = "M400,250";
    let pos = {x:400, y:250};
    let angle = 0;
    let color = "black";
    let stack = [];
    let paths = [];

    for (let i = 0; i < result.length; i++) {
        let symbol = result[i];
        let operation = translations[symbol];
        let parameter;
        if (operation.includes(" ")) {
            let index = operation.indexOf(" ")
            parameter = operation.slice(index+1);
            operation = operation.slice(0,index);
        }

        

        if (operation == "forward") {
            pos.x += parameter * Math.cos(angle);
            pos.y += parameter * Math.sin(angle);
            path += ` M${pos.x.toFixed(2)},${pos.y.toFixed(2)}`;
        }
        else if (operation == "draw") {
            pos.x += parameter * Math.cos(angle);
            pos.y += parameter * Math.sin(angle);
            path += ` L${pos.x.toFixed(2)},${pos.y.toFixed(2)}`;
        }
        else if (operation == "angle") {
            angle += parameter * Math.PI / 180
        }
        else if (operation == "color") {
            paths.push({path, color})
            path = `M${pos.x.toFixed(2)},${pos.y.toFixed(2)}`;
            console.log(parameter)
            if (parameter.includes(" ")) {
                parameter = parameter.split(" ");
                parameter = `rgb(${parameter[0]}, ${parameter[1]}, ${parameter[2]})`;
            }
            color = parameter
        }
        else if (operation == "push") {
            stack.push(new DrawingState(pos.x, pos.y, angle))          
        }
        else if (operation == "pop") {
            drawingState = stack.pop()
            pos.x = drawingState.x
            pos.y = drawingState.y
            angle = drawingState.angle
            path += ` M${pos.x.toFixed(2)},${pos.y.toFixed(2)}`;
        }
        else if (operation == "nop") {      
        }
    }
    paths.push({path, color})
    return paths
}

function parseTranslations(transl) {
    let transl_obj = {};
    transl = transl.split(",")
    for (let i = 0; i < transl.length; i++) {
        const command = transl[i].trim().split(":");
        const key = command[0].trim();
        const value = command[1].trim();
        transl_obj[key] = value;
      }
    return transl_obj
}

let paths = generateSVGPaths(result, translations)

const svg = d3.select("svg")
    .attr("width",2000)
    .attr("height",2000);

for (let i = 0; i < paths.length; i++) {
    svg.append("path")
        .attr("d",paths[i].path)
        .attr("fill","none")
        .attr("stroke",paths[i].color)
        .attr("stroke-width",2)
}
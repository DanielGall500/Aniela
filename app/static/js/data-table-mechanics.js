// Get the button element
let sourceTextbox = document.getElementById("source");
let targetTextbox = document.getElementById("target");
let serverTextbox = document.getElementById("server");
let gpuTextbox = document.getElementById("gpu");
let idTextbox = document.getElementById("id");

function getCurrentSetupAddition() {
    return {
    "src": sourceTextbox.value,
    "tgt": targetTextbox.value,
    "server": serverTextbox.value,
    "gpu": gpuTextbox.value,
    "id": idTextbox.value
    }
}

function addRow() {
    let newModel = getCurrentSetupAddition()

    // Make an HTTP request to the FastAPI endpoint
    fetch('/dashboard/setup/add', {
        method: 'POST',  
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            "src": String(newModel.src), "tgt": String(newModel.tgt), 
            "server": String(newModel.server), "gpu": String(newModel.gpu), 
            "id": String(newModel.id) 
        }),
    })
    window.location.href = "/dashboard/setup"
}

function deleteRow(src, tgt, id) {
    // Make an HTTP request to the FastAPI endpoint
    fetch('/dashboard/setup/delete', {
        method: 'POST', 
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "src": src, "tgt": tgt, "model_id": id }),
    })
    window.location.href = "/dashboard/setup"
}
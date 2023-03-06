function changeValuesClick(input_selected) {
    var inp_name = input_selected.name
    var imp_value = input_selected.value
    if (input_selected.style.backgroundColor === "rgb(248, 249, 250)"){
        input_selected.style.backgroundColor = "rgb(25, 135, 84)";
    }else {
        input_selected.style.backgroundColor = "rgb(248, 249, 250)";
    }
    if (input_selected.style.color === "rgb(0, 0, 0)"){
        input_selected.style.color = "rgb(248, 249, 250)";
    }else {
        input_selected.style.color = "rgb(0, 0, 0)";
    }
    if (input_selected.style.borderColor === "rgb(0, 0, 0)"){
        input_selected.style.borderColor = "rgb(25, 135, 84)";
    }else {
        input_selected.style.borderColor = "rgb(0, 0, 0)";
    }
    if (inp_name === imp_value){
        input_selected.name = "False";
    }else {
        input_selected.name = imp_value;
    }
}
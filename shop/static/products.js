function setAttributeParam(id, value){
    let currValue = document.getElementById('id_'+id).value
    document.getElementById('id_'+id).value = currValue? currValue+"."+value : value;
    document.getElementById("attributeForm").submit()
}

function clearAttributeParam(id, value) {
    var newValue = document.getElementById(id).value.replaceAll(value, "");
    newValue = newValue.startsWith('.') ? newValue.substring(1) : newValue;
    newValue = newValue.endsWith('.') ? newValue.slice(0, -1) : newValue;

    document.getElementById(id).value = newValue.replace('..', '.');
    document.getElementById("attributeForm").submit()
}

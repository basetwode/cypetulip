function setAttributeParam(id, value){
    document.getElementById('id_'+id).value = value;
    document.getElementById("attributeForm").submit()
}

function clearAttributeParam(id) {
    document.getElementById(id).value = "";
    document.getElementById("attributeForm").submit()
}
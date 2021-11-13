function setAttributeParam(key, value) {
    key = encodeURIComponent(key);
    value = encodeURIComponent(value);
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.append(key, value);

    window.location.search = urlParams;
}

function clearAttributeParam(key, value) {
    key = encodeURIComponent(key);
    value = encodeURIComponent(value);
    const urlParams = new URLSearchParams(window.location.search.slice(1));

    var existingParams = urlParams.getAll(key)
    const index = existingParams.indexOf(value)
    if (index > -1) {
        existingParams.splice(index, 1)
    }
    urlParams.delete(key);
    existingParams.forEach(param => urlParams.append(key, param)
    );

    window.location.search = urlParams;
}

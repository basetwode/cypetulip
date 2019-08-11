function addToCart(product) {
    $.ajax({
        url: '/shop/cart/add/' + product,
        method: 'post',
        data: $('#add-cart-form').serialize(),

        success: function (data) {

            $('#shopping-cart').html(data);


        }
    })
}

function submitForm(url, form) {
    var data = $('#' + form);
    console.log(data);
    var formData = new FormData(data[0]);
    if (!data[0].checkValidity()) {

    }
    $('p.error').html("");
    data.find('tr, div').removeClass('error-row');
    data.find(".input-group").removeClass('has-error');
    waitModal = $('#wait-modal');
    waitModal.modal('show');
    $.ajax({
        xhr: function () {
            var xhr = new window.XMLHttpRequest();

            xhr.upload.addEventListener("progress", function (evt) {
                if (evt.lengthComputable) {
                    var percentComplete = evt.loaded / evt.total;
                    percentComplete = parseInt(percentComplete * 100);
                    $('.progress-bar').css('width', percentComplete + '%').attr('aria-valuenow', percentComplete);
                }
            }, false);
            return xhr;
        },
        url: url,
        method: 'post',
        data: formData,
        enctype: 'multipart/form-data',
        processData: false,  // tell jQuery not to process the data
        contentType: false,   // tell jQuery not to set contentType
        success: function (data) {

            console.log(data);
            $('#alert-success').show();
            waitModal.modal('hide');
            $('.progress-bar').css('width', 0 + '%').attr('aria-valuenow', 0);
            var nextForm = $('#next-step-form');
            if(data.next_url.length > 0){
                nextForm.attr('action', data.next_url);
            }
            nextForm.find('#next-step-token').val(data.token);
            nextForm.submit();
            //window.location.href = "/shop/overview/"+data['order']+"/"+data['token']
        },
        error: function (data) {

            $('#alert-warning').hide();
            $('#alert-danger').hide();
            waitModal.modal('hide');
            $('.progress-bar').css('width', 0 + '%').attr('aria-valuenow', 0);
            // $.each(data.responseJSON, function (index, row) {
            //     if (row)
            //         $.each(row, function (index, row) {
            //             if (row && row[0]) {
            //
            //                 //console.log(row[0][0]);
            //                 //console.log(row[0][1]);
            //                 var rowH = $('#' + row[0][0]);
            //                 rowH.addClass('error-row');
            //                 rowH.find(".error").html((row[0][1]));
            //                 rowH.find(".input-group").addClass('has-error');
            //             }
            //         });
            // });
             parseErrors(data);
            //$('.main').html($(data.responseText).find(".main").html())
        }
    })


}

function addToSubTotal(product, subproductPrice) {
    var productPrice = parseInt($('#subtotal-' + product).html(), 10)
    productPrice += subproductPrice;
    var total = parseInt($('#total').html(), 10);
    total += subproductPrice;
    $('#total').html(total);
    $('#subtotal-' + product).html(productPrice + " &euro;");
}

function duplicateProduct(button, product, price) {
    var row = button.parentNode.parentNode;
    var newRow = $(row).clone(true);
    $(row).find("button").remove();
    //inputs = $(newRow).find("input");
    //for(element in inputs ){
    //    $(element).val("");
    //}
    $(newRow).insertBefore(row.nextSibling);
    addToSubTotal(product, price)
}


function parseErrors(data) {

    message = data.responseJSON;
    success = message.success;
    errors = message.errors;
    errorCode = 0;
    for(index = 0; index < errors.length; index++){
        error = errors[index];
        input_element = $('#'+error.field_name);
        input_element.addClass('error-row');
        input_element.find('.error').html(error.message);
        input_element.find('.input-group, .form-group').addClass('has-error');
        if(errorCode < error.code){
            errorCode=error.code;
        }
    }
    switch(errorCode){
        case 400:
            $('#alert-warning').show();
            break;
        case 500:
            $('#alert-danger').show();
    }
}
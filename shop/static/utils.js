function addToCart(product) {
    $.ajax({
        url: '/shop/cart/add/' + product,
        method: 'post',
        data: $('#add-cart-form').serialize(),

        success: function (data) {
            // $('#shopping-cart').html(data);
        }
    })
}

function submitForm(url, form) {
    var data = $("#" + form);
    var formData = new FormData(data[0]);
    // if (!data[0].checkValidity()) {
    //
    // }
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
        type: 'POST',
        method: 'POST',
        data: formData,
        enctype: 'form/multipart',
        processData: false,  // tell jQuery not to process the data
        contentType: false,   // tell jQuery not to set contentType
        success: function (response) {

            console.log('success: ', response);
            $('#alert-success').show();
            waitModal.modal('hide');
            $('.progress-bar').css('width', 0 + '%').attr('aria-valuenow', 0);
            var nextForm = $('#next-step-form');
            if (response.next_url.length > 0) {
                nextForm.attr('action', response.next_url);
            }
            nextForm.find('#next-step-token').val(response.token);
            nextForm.submit();
            // window.location.href = "/shop/overview/" + response['order'] + "/" + response['token']
        },
        error: function (response) {
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
            parseErrors(response);
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
    for (index = 0; index < errors.length; index++) {
        error = errors[index];
        input_element = $('#' + error.field_name);
        input_element.addClass('error-row');
        input_element.find('.error').html(error.message);
        input_element.find('.input-group, .form-group').addClass('has-error');
        if (errorCode < error.code) {
            errorCode = error.code;
        }
    }
    switch (errorCode) {
        case 400:
            $('#alert-warning').show();
            break;
        case 500:
            $('#alert-danger').show();
    }
}

$(function () {


    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url === origin || url.slice(0, origin.length + 1) === origin + '/') ||
            (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});
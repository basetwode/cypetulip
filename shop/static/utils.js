function addToCart(url) {
    const loadingSpinner = $('#loading-spinner');
    loadingSpinner.removeClass('overlay-hidden');
    $.ajax({
        url: url,
        method: 'post',
        data: $('#add-cart-form').serialize(),

        success: function (data) {
            $('#alert-success').show();
            $('#shopping-cart').html(data);
            loadingSpinner.addClass('overlay-hidden');
        },
        error: function (response) {
            loadingSpinner.addClass('overlay-hidden');
            $('#alert-danger').show();
            setTimeout(() => {
                const message = response.responseJSON;
                let nextUrl = message.next_url;
                window.location.replace(nextUrl);
            }, 1000)

        }
    });
}

function submitForm(url, form) {
    var data = $("#" + form);
    var formData = new FormData(data[0]);
    $('p.error').html("");
    data.find('tr, div').removeClass('error-row');
    data.find(".input-group").removeClass('has-error');
    loadingSpinner = $('#loading-spinner');
    loadingSpinner.removeClass('overlay-hidden');
    $.ajax({
        url: url,
        type: 'POST',
        method: 'POST',
        data: formData,
        enctype: 'form/multipart',
        processData: false,  // tell jQuery not to process the data
        contentType: false,   // tell jQuery not to set contentType
        success: function (response) {
            $('#alert-success').show();
            loadingSpinner.addClass('overlay-hidden');
            var nextForm = $('#next-step-form');
            if (response.next_url.length > 0) {
                nextForm.attr('action', response.next_url);
                nextForm.attr('method','get');
            }
            nextForm.find('#next-step-token').val(response.token);
            nextForm.submit();
        },
        error: function (response) {
            $('#alert-warning').hide();
            $('#alert-danger').hide();
            loadingSpinner.addClass('overlay-hidden');
            $('.progress-bar').css('width', 0 + '%').attr('aria-valuenow', 0);
            parseErrors(response);
        }
    });


}
function parseErrors(data) {
    const positionTop = 0;
    const message = data.responseJSON;
    const success = message.success;
    let errors = message.errors;
    let errorCode = 0;
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
            $(window).scrollTop(positionTop);
            break;
        case 500:
            $('#alert-danger').show();
            $(window).scrollTop(positionTop);
            break;
    }
}


function assignEmployee(uuid) {
    var id = $('#employee-select').val();
    $.ajax(
        {
            url: uuid + '/assign/',
            method: 'post',
            data: $('#assignEmployeeForm').serialize() + '&id=' + id,
            success: function () {
                $('#alert-success').show();
                $('#assign-employee-modal').modal('hide');
                setTimeout(() => {
                    window.location.reload()
                }, 1000)
            },
            error: function () {
                $('#alert-danger').show();
            }
        }
    )
}

function changeState(uuid) {
    var id = $('#change-state-select').val();
    $.ajax(
        {
            url: uuid + '/states/change',
            method: 'post',
            data: $('#changeStateForm').serialize() + '&id=' + id,
            success: function () {
                $('#alert-success').show();
                $('#change-state-modal').modal('hide');
                setTimeout(() => {
                    window.location.reload()
                }, 1000)
            },
            error: function () {
                $('#alert-danger').show();
            }
        }
    )
}

$(function () {


    // This function gets cookie with a given name
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                let cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    let csrftoken = getCookie('csrftoken');

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
        const host = document.location.host; // host + port
        const protocol = document.location.protocol;
        const sr_origin = '//' + host;
        const origin = protocol + sr_origin;
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

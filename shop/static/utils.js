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

/**
 * Created by ansel on 1/29/2016.
 */

function loadPage(page,title) {
    $.ajax({
        url: page,
        method: 'GET',

        success: function (data) {

            $('#main').html(data);
            document.title = title;
            document.href = page;
        },
        error: function () {
        }

    });
}
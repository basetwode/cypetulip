/**
 * Created by Anselm on 2/18/2016.
 */

$(document).ready(function () {
    $('#accordion').on('show.bs.collapse', function (e) {
        // $('#accordion').find('input[checked]').removeProp('checked');
        var id = e.target.id.toString();
        id = id.substring(id.length - 1, id.length);
        $(this).find('#input' + id).prop('checked', true);
    }).on('show.bs.collapse', function (e) {
            $(e.target).prev('.panel-heading').addClass('active');
    }).on('hide.bs.collapse', function (e) {
            $(e.target).prev('.panel-heading').removeClass('active');
    });
});

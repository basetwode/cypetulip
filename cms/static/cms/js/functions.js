/**
 * Created by Anselm on 2/2/2016.
 */


function setLanguage(lang) {
    $.ajax(
        {
            url: '/shop/i18n/setlang/',
            method: 'post',
            data: $('#lang-form').serialize() + '&language=' + lang,
            success: function () {
                location.reload()
            }
        }
    )
}
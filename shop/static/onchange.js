/**
 * Created by ansel on 1/5/2017.
 */
function changeNumberOfOrders(form, url) {
    select = $(form);
    var url_formatted = String.format(url,select.val());
    select.parent().attr('action',url_formatted);
    select.parent().submit();
    console.log(url_formatted);
}

String.format = function() {
      var s = arguments[0];
      for (var i = 0; i < arguments.length - 1; i++) {
          var reg = new RegExp("\\{" + i + "\\}", "gm");
          s = s.replace(reg, arguments[i + 1]);
      }
      return s;
  }
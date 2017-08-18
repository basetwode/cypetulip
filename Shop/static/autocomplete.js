/**
 * Created by ansel on 1/4/2017.
 */
$(function() {

    $("#order-search").autocomplete({

        source: function(request, response) {
            $.ajax({
                url: 'orders/search/',
                data: {search: request.term },
                dataType: "json",
                success: function(data) {
                    a=[]
                    for ( i = 0; i < data.length; i++) {
                        a.push({label:"Order "+data[i].fields.order_hash, value:data[i].fields.order_hash});
                    }
                    response(a);

                }
            });
        },

        minLength: 1,

        select: function(event, ui) {
            var url = ui.item.value;
            if(url != '#') {
                location.href = '/shop/myaccount/orders/' + url;
            }
        },

        html: true, // optional (jquery.ui.autocomplete.html.js required)

      // optional (if other layers overlap autocomplete list)
        open: function(event, ui) {
            $(".ui-autocomplete").css("z-index", 1000);
        }
    });

});
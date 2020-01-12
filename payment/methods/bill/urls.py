from django.conf.urls import url

from payment.methods.bill.views import BillConfirmView, BillSubmitView

app_name = 'bill'

urlpatterns = [
    url(r"^$", BillConfirmView.as_view(), name="index"),
    url(r"^submit/$", BillSubmitView.as_view(), name="submit"),
]

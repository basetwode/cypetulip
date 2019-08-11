from django.conf.urls import url, include

from payment.methods.bill.views import BillConfirmView, BillSubmitView

urlpatterns = [
    url(r"^$", BillConfirmView.as_view(),name="bill"),
    url(r"^submit/$", BillSubmitView.as_view(), name="bill_submit"),
]
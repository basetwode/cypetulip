from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View

from shop.errors import JsonResponse
from shop.models import Contact, Order, OrderItem, Product, ProductSubItem, Address, Company
from shop.order.forms import ItemBuilder, SubItemForm, OrderDetail, AddressForm, ContactForm
from shop.utils import create_hash, json_response

__author__ = 'Anselm'


class DeliveryView(View):
    template_name = 'order/delivery.html'

    def delete(self, request, product_id):
        if request.user.is_authenticated:
            instance = OrderItem.objects.get(id=product_id)
            instance.delete()
        else:
            instance = OrderItem.objects.get(id=product_id)
            instance.delete()
        return render(request, self.template_name)

    def get(self, request, order):
        orders = None
        address = None
        if request.user.is_authenticated:
            contact = Contact.objects.filter(user=request.user)
            address = Address.objects.filter(contact=contact[0])
            company = contact[0].company
            orders = Order.objects.filter(order_hash=order, is_send=False, company=company)
        else:
            orders = Order.objects.filter(order_hash=order, is_send=False)
            order_details = OrderDetail.objects.get(order=orders[0])
            if order_details.shipment_address:
                address = Address.objects.filter(id=order_details.shipment_address.id)
            else:
                address = None
        if orders.count() > 0:
            order = orders[0]
            sub_order_items = OrderItem.objects.filter(order=order).exclude(product__in=Product.objects.all())
            sub_order_items.delete()
            sub_products_once_only = self.get_subproducts_once_only(order)
            address_form = AddressForm()
            contact_form = ContactForm()
            return render(request, self.template_name, {'order_details': order,
                                                        'sub_products_once_only': sub_products_once_only,
                                                        'address': address, 'addressForm': address_form,
                                                        'contactForm': contact_form})
        else:
            return redirect(reverse('shop:shopping_cart'))

    def post(self, request, order):
        _order = None
        order_details = None
        contact_by_user = None
        if request.user.is_anonymous:
            contact_from_visitor = Contact.objects.filter(first_name=request.POST['first_name'],
                                                          last_name=request.POST['last_name'],
                                                          email=request.POST['email'])
            contact_by_user = contact_from_visitor
            if not contact_from_visitor:
                new_company = Company(name=request.POST['email'], term_of_payment=10, street=request.POST['name'],
                                      number=request.POST['name'], zipcode=request.POST['name'],
                                      city=request.POST['name'])
                new_company.save()
                new_contact = Contact(first_name=request.POST['first_name'], last_name=request.POST['last_name'],
                                      gender=request.POST['gender'], email=request.POST['email'],
                                      telephone=request.POST['telephone'], company=new_company)
                new_contact.save()
                contact_by_user = new_contact
                address_by_form = Address(name=request.POST['name'], street=request.POST['name'],
                                          number=request.POST['name'], zipcode=request.POST['name'],
                                          city=request.POST['name'], contact=new_contact)
                address_by_form.save()
                _order = Order.objects.filter(order_hash=order, is_send=False)
                _order[0].company = new_company
                _order[0].save()
                order_details = OrderDetail.objects.get(order=_order[0])
                order_details.shipment_address = address_by_form
                _order = Order.objects.filter(order_hash=order, is_send=False)

            else:
                _order = Order.objects.filter(order_hash=order, is_send=False)
                order_details = OrderDetail.objects.get(order=_order[0])
        else:
            contact_by_user = Contact.objects.filter(user=request.user)
            company = contact_by_user[0].company
            _order = Order.objects.filter(order_hash=order, is_send=False, company=company)
            order_details = OrderDetail.objects.get(order_number=order)
        if _order.count() > 0:

            token = create_hash()
            # TODO: check if anything is added, else add errors to show
            if request.POST.get("shipment-address"):
                shipment_address = Address.objects.get(id=request.POST.get("shipment-address"))
            else:
                shipment_address = Address(name=request.POST['name'], street=request.POST['street'],
                                           number=request.POST['number'], zipcode=request.POST['zipcode'],
                                           city=request.POST['city'], contact=contact_by_user[0])
                shipment_address.save()
            order_details.shipment_address = shipment_address
            order_details.save()
            ord = _order[0]
            ord.token = token
            ord.save()
            # result = json_response(code=200, x=JsonResponse(token=token).dump())
            # return result
            return json_response(200, x={'token': token, 'order': _order[0].order_hash, 'next_url': '', })
        else:
            errors = []
            result = json_response(code=400, x=JsonResponse(success=False, errors=errors).dump())
            return result

    def create_form(self, request, all_forms, key, value, **kwargs):
        item_builder = ItemBuilder()
        order_item = item_builder.build(key, value)

        if order_item:
            form = self.create_order_item(order_item=order_item, request=request)
            if form:
                all_forms.setdefault("{}-{}{}".format(order_item.get("order_item"), order_item['product'],
                                                      '-{}'.format(kwargs.get('index')) if kwargs.get(
                                                          'index') and kwargs.get(
                                                          'index') > 0 else ''), form)
            return form

    def create_order_item(self, order_item, request):
        item_type = order_item.pop('product_type')
        form = SubItemForm(item_type, order_item, request)
        return form

    def get_subproducts(self, order):
        order_items = OrderItem.objects.filter(order=order, product__id__in=Product.objects.all())
        assigned_sub_products = order_items.values('product')
        assigned_sub_products = Product.objects.filter(id__in=assigned_sub_products)
        sub_products_once_only = ProductSubItem.objects.filter(
            id__in=assigned_sub_products.values('assigned_sub_products')
        )
        return sub_products_once_only

    def get_subproducts_once_only(self, order):
        sub_products_once_only = self.get_subproducts(order)
        sub_products_once_only = sub_products_once_only.filter(is_required=True, is_once_per_order=True)
        return sub_products_once_only

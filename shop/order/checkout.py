from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View

from shop.Errors import FieldError, JsonResponse
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

        return render(request, self.template_name)

    def get(self, request, order):
        orders = None
        if request.user.is_authenticated:
            contact = Contact.objects.filter(user=request.user)
            address = Address.objects.filter(contact=contact[0])
            company = contact[0].company
            orders = Order.objects.filter(order_hash=order, is_send=False, company=company)
        else:
            orders = Order.objects.filter(order_hash=order, is_send=False)
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
        # TODO add new contact and address from delivery form

        _order = None
        order_details = None
        if request.user.is_anonymous:
            contact_from_visitor = Contact.objects.filter(first_name=request.POST['first_name'],
                                                          last_name=request.POST['last_name'],
                                                          email=request.POST['email'])

            if not contact_from_visitor:
                new_company = Company(name=request.POST['email'])
                new_contact = Contact(first_name=request.POST['first_name'], last_name=request.POST['last_name'],
                                      gender=request.POST['gender'], email=request.POST['email'],
                                      telephone=request.POST['telephone'], company=new_company)
                address_by_form = Address(name=request.POST['name'], street=request.POST['name'],
                                          number=request.POST['name'], zipcode=request.POST['name'],
                                          city=request.POST['name'], contact=new_contact)
                _order = Order.objects.filter(order_hash=order, is_send=False)
                _order[0].company = new_company
                _order[0].save()
                _order_details = OrderDetail.objects.get(order=_order[0])
                _order_details.shipment_address = address_by_form
            else:
                pass
        else:
            contact_by_user = Contact.objects.filter(user=request.user)
            company = contact_by_user[0].company
            _order = Order.objects.filter(order_hash=order, is_send=False, company=company)
            order_details = OrderDetail.objects.get(order_number=order)
        if _order.count() > 0:
            forms = {}
            forms_are_valid = True
            for post in request.FILES:
                values = request.FILES.getlist(post)
                file_index = 0
                for value in values:
                    form = self.create_form(request, forms, post, value,
                                            index=file_index)
                    file_index += 1
                    if form:
                        forms_are_valid = forms_are_valid and form.is_valid()
            for post in request.POST:
                value = request.POST.get(post)
                # TODO this items can also be multiple, check that

                form = self.create_form(request, forms, post, value)
                if form:
                    forms_are_valid = forms_are_valid and form.is_valid()

            if forms_are_valid:
                for k, v in forms.items():
                    v.save()
                token = create_hash()
                if request.POST.get("shipment-address"):
                    shipment_address = Address.objects.get(id=request.POST.get("shipment-address"))
                else:
                    shipment_address = Address(name=request.POST['name'], street=request.POST['name'],
                                               number=request.POST['name'], zipcode=request.POST['name'],
                                               city=request.POST['name'], contact=contact_by_user[0])
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
                # return json_response(code=400, x={'success': False,
                #                                   'errors': [([(formkey, v[0]) for k, v in form.errors.items()]) for
                #                                              formkey, form
                #                                              in forms.items()]
                #                                   })
                errors = []
                for formkey, form in forms.items():
                    errors_form = [FieldError(message=v[0], field_name=formkey) for k, v in form.errors.items()]
                    errors.extend(errors_form)

                # errors = [[FieldError(message=v[0], field_name=k) for k, v in form.errors.items()] for
                #           formkey, form
                #           in forms.items()]

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

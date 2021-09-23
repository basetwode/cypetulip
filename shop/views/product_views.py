import operator
from functools import reduce

from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Q, Prefetch
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.generic import ListView, FormView, DetailView

from cms.models.main import Section
from home.settings import CACHE_MIDDLEWARE_SECONDS
from shop.forms.product_forms import ProductAttributeForm, IndividualOfferForm
from shop.models.accounts import Contact
from shop.models.products import ProductCategory, ProductAttributeType, ProductAttributeTypeInstance, Product, \
    ProductImage
# Create your views here.
from shop.views.mixins import TaxView, EmailNotifyStaffView


@method_decorator(vary_on_headers('User-Agent', 'Cookie'), name='dispatch')
@method_decorator(cache_page(CACHE_MIDDLEWARE_SECONDS), name='dispatch')
class ProductView(TaxView, ListView):
    template_name = 'shop/products/products-product-overview.html'
    context_object_name = 'products'
    paginate_by = 18

    def _get_url_page(self, products_list, page):
        paginator = Paginator(products_list, self.paginate_by)
        try:
            url_list = paginator.page(page)
        except PageNotAnInteger:
            url_list = paginator.page(1)
        except EmptyPage:
            url_list = paginator.page(paginator.num_pages)
        return url_list

    def get_queryset(self):
        selected_category = None
        if 'category' in self.kwargs:
            selected_category = ProductCategory.objects.get(path=self.kwargs['category'])
            relevant_categories = ProductCategory.objects.filter(path__startswith=selected_category.path)
            products = Product.objects.filter(is_public=True, category__in=relevant_categories)
        if not selected_category:
            products = Product.objects.filter(is_public=True)

        product_attribute_categories = ProductAttributeType.objects. \
            filter(productattributetypeinstance__product__in=products).annotate(count=Count('name', distinct=True))
        attribute_form = ProductAttributeForm(product_attribute_categories, self.request.GET)

        attribute_filter = (reduce(operator.or_, (Q(type__name=k, value=v_spl) for v_spl in v.split('.'))) for k, v in
                            self.request.GET.items()) \
            if len(self.request.GET) > 0 else None

        selected_attributes = ProductAttributeTypeInstance.objects.filter(reduce(operator.or_, attribute_filter)) \
            if attribute_filter else []

        for type in ProductAttributeType.objects.filter(
                productattributetypeinstance__in=selected_attributes).distinct():
            products = products.filter(attributes__id__in=selected_attributes.filter(type=type))

        return products.order_by('id').prefetch_related(
            Prefetch('productimage_set', queryset=ProductImage.objects.order_by('id')),
            'attributes', 'discount_set', )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)

        sections = Section.objects.filter(page__page_name="Products")

        categories = ProductCategory.objects.filter(is_main_category=True).prefetch_related('productcategory_set')
        products = self.object_list

        product_attribute_categories = ProductAttributeType.objects. \
            filter(productattributetypeinstance__product__in=products).annotate(count=Count('name', distinct=True))
        attribute_form = ProductAttributeForm(product_attribute_categories, self.request.GET)

        # Update available list of attributes
        product_attribute_categories = ProductAttributeType.objects. \
            filter(productattributetypeinstance__product__in=products).annotate(count=Count('name', distinct=True))
        product_attribute_types = ProductAttributeTypeInstance.objects.all(). \
            annotate(count=Count('product', filter=Q(product__in=products)))

        products = self._get_url_page(products, self.request.GET.get('page'))

        selected_category = ''
        if 'category' in self.kwargs:
            selected_category = ProductCategory.objects.get(path=self.kwargs['category'])

        return {**context, **{'sections': sections, 'products': products,
                              'categories': categories,
                              'types': product_attribute_categories,
                              'type_instances': product_attribute_types,
                              'attribute_form': attribute_form,
                              'selected_category': selected_category}}


class ProductDetailView(DetailView):
    template_name = 'shop/products/products-product-detail.html'
    model = Product

    def get_object(self, queryset=None):
        selected_product = Product.objects.filter(is_public=True, name=self.kwargs['product'],
                                                  category__path=self.kwargs['category'])
        if selected_product.count() > 0:
            selected_product = selected_product[0]
        return selected_product

    def get_context_data(self, **kwargs):
        categories = ProductCategory.objects.filter(is_main_category=True)
        return {**super(ProductDetailView, self).get_context_data(**kwargs), **{'categories': categories}}


class IndividualOfferView(EmailNotifyStaffView, FormView):
    email_template = "shop/mail/mail-newindividualofferrequest.html"
    subject = _("New individual offer request")
    form_class = IndividualOfferForm
    template_name = 'shop/products/products-product-individualoffer.html'
    success_url = reverse_lazy('shop:products', kwargs={'category': ''})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(name=self.kwargs['product'],
                                                 category__path=self.kwargs['category'])
        return context

    def get_initial(self, form_class=None):

        initial = super().get_initial()
        if self.request.user.is_authenticated:
            contact = Contact.objects.get(user_ptr=self.request.user)
            initial['mail'] = contact.email
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.request.user.is_authenticated:
            self.object.contact = Contact.objects.get(user_ptr=self.request.user)
        self.object.product = Product.objects.get(name=self.kwargs['product'],
                                                  category__path=self.kwargs['category'])
        self.object.save()
        self.notify()
        messages.success(self.request, _("Thank you for your request, we'll contact you soon"))
        return HttpResponseRedirect(self.get_success_url())

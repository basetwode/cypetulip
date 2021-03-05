import random
from urllib.request import urlopen

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management import BaseCommand

from shop.models.products import ProductCategory, ProductAttributeTypeInstance, Product, ProductImage


class Command(BaseCommand):
    help = "Inserts demo data, might take a while on first run since it downloads random images"

    def handle(self, *args, **kwargs):
        category1, _ = ProductCategory.objects.get_or_create(name="Men", description="Mens clothing",
                                                             is_main_category=True)
        category1.save()
        category11, _ = ProductCategory.objects.get_or_create(name="Shirts", description="Shirts",
                                                              mother_category=category1)
        category11.save()
        category12, _ = ProductCategory.objects.get_or_create(name="Underwear", description="Underwear",
                                                              mother_category=category1)
        category12.save()
        category13, _ = ProductCategory.objects.get_or_create(name="Trousers", description="Trousers",
                                                              mother_category=category1)
        category13.save()
        category1.child_categories.add(category11)
        category1.child_categories.add(category12)
        category1.child_categories.add(category13)
        category1.save()
        category2, _ = ProductCategory.objects.get_or_create(name="Women", description="Womens clothing",
                                                             is_main_category=True)
        category2.save()
        category21, _ = ProductCategory.objects.get_or_create(name="Shirts", description="Shirts",
                                                              mother_category=category2)
        category21.save()
        category22, _ = ProductCategory.objects.get_or_create(name="Underwear", description="Underwear",
                                                              mother_category=category2)
        category22.save()
        category23, _ = ProductCategory.objects.get_or_create(name="Trousers", description="Trousers",
                                                              mother_category=category2)
        category23.save()
        category2.child_categories.add(category21)
        category2.child_categories.add(category22)
        category2.child_categories.add(category23)
        category2.save()

        # todo assigned subproducts und attributes
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

        for category in ProductCategory.objects.filter(mother_category__isnull=False):
            for i in range(0, 200):
                special_price_yes = True if random.randint(0, 10) > 8 else False
                price = random.randint(6, 70)
                product = Product.objects.filter(stock=10, max_items_per_order=5, category=category, is_public=True,
                                                 description=text,
                                                 details=text,
                                                 name=category.name + "-" + str(i))
                _created = False
                if product.count() == 0:
                    product = Product(stock=10, max_items_per_order=5, category=category, is_public=True,
                                      description=text,
                                      details=text,
                                      name=category.name + "-" + str(i))
                    _created = True
                else:
                    product = product.first()
                product.special_price = random.randint(6, price) if special_price_yes else 0
                product.price = price
                product.save()

                pi, _created = ProductImage.objects.get_or_create(product=product)
                if _created:
                    image_url = "https://picsum.photos/400/600"
                    img_temp = NamedTemporaryFile()
                    img_temp.write(urlopen(image_url).read())
                    img_temp.flush()
                    #

                    pi.product_picture.save("image.jpg", File(img_temp))
                    pi.save()

                p_attributes = ProductAttributeTypeInstance.objects.filter(type__name="Marke")
                product.attributes.clear()
                if p_attributes.count() > 0:
                    product.attributes.add(p_attributes.order_by('?').first())

                p1_attributes = ProductAttributeTypeInstance.objects.filter(type__name="Spezialgrößen")
                if p1_attributes.count() > 0:
                    product.attributes.add(p1_attributes.order_by('?').first())

                p2_attributes = ProductAttributeTypeInstance.objects.filter(type__name="Style")
                if p2_attributes.count() > 0:
                    product.attributes.add(p2_attributes.order_by('?').first())

                p3_attributes = ProductAttributeTypeInstance.objects.filter(type__name="Material")
                if p3_attributes.count() > 0:
                    product.attributes.add(p3_attributes.order_by('?').first())

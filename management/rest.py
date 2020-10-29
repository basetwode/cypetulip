from rest_framework import routers, viewsets, serializers

from shop.models import Product, ProductCategory, ProductAttributeType, ProductAttributeTypeInstance, ProductSubItem
from shop.rest import AddressViewSet, AccountViewSet, ContactViewSet


class ProductAttributeTypeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ProductAttributeType
        fields = '__all__'


class ProductAttributeTypeInstanceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ProductAttributeTypeInstance
        fields = '__all__'


class ProductCategorySerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = '__all__'


class ProductSubItemSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ProductSubItem
        fields = '__all__'


###############################################################


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductAttributeTypeViewSet(viewsets.ModelViewSet):
    queryset = ProductAttributeType.objects.all()
    serializer_class = ProductAttributeTypeSerializer


class ProductAttributeTypeInstanceViewSet(viewsets.ModelViewSet):
    queryset = ProductAttributeTypeInstance.objects.all()
    serializer_class = ProductAttributeTypeInstanceSerializer


class ProductSubItemViewSet(viewsets.ModelViewSet):
    queryset = ProductSubItem.objects.all()
    serializer_class = ProductSubItemSerializer


router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', ProductCategoryViewSet)
router.register(r'productattributetypes', ProductAttributeTypeViewSet)
router.register(r'productattributetypeinstances', ProductAttributeTypeInstanceViewSet)
router.register(r'productsubitem', ProductSubItemViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'contacts', ContactViewSet)

from django.apps import AppConfig



class ShippingConfig(AppConfig):
    name = 'shipping'

    def ready(self):
        try:
            from shipping.models import Region
            from shipping.models import Country, Continent, Shipper
            region_europe = Region.objects.filter(name="Europe")
            if region_europe.count() == 0:
                region_europe = Region(name="Europe", countries="")
                region_europe.save()
            else:
                region_europe = region_europe[0]

            continent_europe, created = Continent.objects.get_or_create(name="Europe")

            country_de = Country.objects.filter(name="Germany")
            if country_de.count() == 0:
                country_de = Country(name="Germany", code="DE", continent=continent_europe)
                country_de.save()
            else:
                country_de = country_de[0]

            shipper = Shipper.objects.filter(code="DHL", name="DHL")
            if shipper.count() == 0:
                shipper = Shipper(code="DHL", name="DHL", region=region_europe, country=country_de)
                shipper.save()
        except:
            print("DB not migrated")
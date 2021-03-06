from django.apps import apps, AppConfig


class BaseConfig(AppConfig):
    api = {'shop':
        {
            'account.orders.order.buttons': {}
        }
    }

    def ready(self):
        self.load_app_apis()

    def load_app_apis(self):
        for app in apps.get_app_configs():
            if hasattr(app, 'api') and self.name in app.api:
                for key, value in self.api[self.name].items():
                    self.api[self.name][key] = {**self.api['shop'][key], **app.api[self.name][key]}

    def get_api_attribute(self, path):
        return self.api[self.name][path]
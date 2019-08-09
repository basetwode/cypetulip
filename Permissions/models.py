from django.contrib.auth.models import User
from django.db import models


class App(models.Model):
    # if an app is specified as public every new user will get normal access to it.
    is_public = models.BooleanField(default=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AppPermission(models.Model):
    # administrators can change settings for this app
    is_administrator = models.BooleanField(default=False)
    # shop employees can see more in this app.
    is_shop_employee = models.BooleanField(default=False)
    # user can access the normal sites of this app.
    can_access_app = models.BooleanField(default=False)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class AppUrl(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    url = models.CharField(max_length=200)
    name = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return str(self.name) + " | " + str(self.url)


class AppUrlPermission(models.Model):
    url = models.ForeignKey(AppUrl, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_access = models.BooleanField(default=True)
    get_access = models.BooleanField(default=True)
    post_message = models.CharField(max_length=400,
                                    default="You don't have the required permissions to do any changes in this view. If you think this is wrong please contact our support")
    get_message = models.CharField(max_length=400,
                                   default="You don't have the required permissions to show this view. If you think this is wrong please contact our support")

    def __str__(self):
        return "%s - P:%s G:%s - %s" % (self.user.username, self.post_access, self.get_access, self.url.url)

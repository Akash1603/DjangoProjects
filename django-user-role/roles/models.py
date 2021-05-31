from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    class Meta:
        db_table = "roles"

    CUSTOMER = 1
    ADMIN = 2
    ROLE_CHOICES = (
        (CUSTOMER, "customer"),
        (ADMIN, "admin"),
    )

    name = models.CharField(choices=ROLE_CHOICES, max_length=25)


class User(AbstractUser):
    class Meta:
        db_table = "users"
        unique_together = ("email",)
        ordering = ["-id"]

    roles = models.ManyToManyField(Role, related_name="user_roles")
    name = models.CharField(max_length=255, null=True)
    mobile = models.CharField(max_length=15, null=True, unique=True)
    avatar = models.ImageField(upload_to="users/avatars/", null=True, blank=True)
    country_code = models.CharField(max_length=5, null=True)
    status = models.CharField(
        choices=[("active", "active"), ("inactive", "inactive")],
        max_length=25,
        default="active",
    )
    is_verify = models.BooleanField(default=False)
    address = models.CharField(max_length=255, null=True)
    lat = models.DecimalField(max_digits=11, decimal_places=2, null=True)
    long = models.DecimalField(max_digits=11, decimal_places=2, null=True)
    device_id = models.CharField(max_length=255, null=True)
    device_key = models.CharField(max_length=255, null=True)
    device_type = models.CharField(
        choices=[("ios", "ios"), ("android", "android"), ("web", "web")],
        max_length=20,
        default="web",
    )

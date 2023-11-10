from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField


class BaseModel(models.Model):
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    avatar = models.ImageField()
    role = models.ForeignKey('Role', related_name="user", on_delete=models.CASCADE, default=1)


class UserInfo(models.Model):
    country = models.CharField(max_length=50, null=False)
    city = models.CharField(max_length=50, null=False)
    street = models.CharField(max_length=50, null=False)
    home_number = models.CharField(max_length=50, null=False)
    phone_number = models.CharField(max_length=10, null=False)
    user = models.OneToOneField(User, related_name="userinfo", on_delete=models.CASCADE, primary_key=True)


class Role(models.Model):
    name = models.CharField(max_length=20)


# Create your models here.


class Product(BaseModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    detail = models.JSONField(null=False)
    old_price = models.DecimalField(max_digits=6, decimal_places=2)
    new_price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey('Category', related_name="product_cate", on_delete=models.CASCADE)
    brand = models.ForeignKey('Brand', related_name="product_brand", blank=True, null=True, on_delete=models.CASCADE)
    # related_name hỗ trợ truy vấn ngươc
    # Ví dụ đứng tu brand muốn tìm tất cả product đang active từ brand đó
    # Brand.Ojects.filter(product-brand__active=True)
    # Ví dụ đứng tu cate muốn tìm tất cả product của cate đó
    # c = Category.Objects(pk=1)   c.product-cate.all()

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Image(models.Model):
    file = models.ImageField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    preview = models.BooleanField(blank=False, default=False)
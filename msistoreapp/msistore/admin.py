from django.contrib import admin
from .models import User, Product, Image, Category

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Image)
admin.site.register(Category)

# Register your models here.

from rest_framework import serializers
from .models import User, Product, Category, Brand, Image
from cloudinary.uploader import upload


class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source='avatar')

    def get_image(self, user):
        if user.avatar:
            request = self.context.get('request')
            return request.build_absolute_uri(user.avatar) if request else ''

    # validated_data: la toan bo du lieu client gui len vd: {first_name: The Anh, last_name: Nguyen...}
    def create(self, validated_data):
        # canh 1:
        # user = User()
        # user.first_name = validated_data['first_name']
        # user.last_name = validated_data['last_name']
        # user.set_password(validated_data['password'])
        # user.save()
        # Cach 2:

        data = validated_data.copy()
        u = User(**data)
        u.set_password(u.password)

        image_file = data['avatar']
        result = upload(image_file)
        u.avatar = result['url']

        u.save()
        return u

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'image', 'avatar', 'email']
        extra_kwargs = {
            'password': {'write_only': True},
            'avatar': {'write_only': True},
        }


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(source='file')

    def get_url(self, image):
        if image.file:
            request = self.context.get('request')
            return request.build_absolute_uri(image.file) if request else ''

    class Meta:
        model = Image
        fields = ['id', 'file', 'product','url', 'preview']
        extra_kwargs = {
            'file': {'write_only': True},
        }

    def create(self, validated_data):
        data = validated_data.copy()
        image = Image(**data)

        image_file = data['file']
        result = upload(image_file)
        image.file = result['url']

        image.save()
        return image


class ProductSerializer(serializers.ModelSerializer):
    # Cach de lay brand(id, name) gắn vao view luôn thay vì chỉ lấy id
    # brand = BrandSerializer()

    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        # obj = product
        request = self.context.get('request')
        i = Image.objects.filter(product=obj).values()
        urls = []
        for data in i:
            urls.append(request.build_absolute_uri(data['file']))
        if request:
            return urls

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'detail', 'old_price', 'new_price', 'category', 'brand', 'images']

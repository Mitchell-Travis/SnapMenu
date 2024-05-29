from django.db import models
from PIL import Image, ImageDraw, ImageFont
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from accounts.models import User
from django.conf import settings
from decimal import Decimal
from .qrcode_generator import generate_qrcode
from django.core.files import File


# Create your models here.
class Restaurant(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=40,null=True,blank=True)
    logo_pic= models.ImageField(upload_to='logo_pic/RestaurantLogo/',null=True,blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=20,null=False)
    @property
    def get_name(self):
        return self.restaurant_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.restaurant_name

    def get_total_orders(self):
        return Orders.objects.filter(restaurant=self).count()

class Customer(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/CustomerProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name


class Table(models.Model):
    table_number = models.IntegerField(null=True, blank=True)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='table', null=True, blank=True)
    qrcode_image = models.ImageField(upload_to='core/table_qrcodes', blank=True)


    def save(self, *args, **kwargs):
        if not self.qrcode_image:
            # Generate the QR code using the utility function
            image_filename, image_buffer = generate_qrcode(self)
            
            # Save the image to the model's field
            self.qrcode_image.save(image_filename, File(image_buffer), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Table {self.table_number}"


class Category(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )
    
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def product_count(self):
        return self.product_set.count()  # This calculates the count of products in this category

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    )
    name=models.CharField(max_length=40)
    product_image= models.ImageField(upload_to='product_image/',null=True,blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description=models.CharField(max_length=200)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    pub_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')


    # New fields for promotions
    has_promo = models.BooleanField(default=False)
    promo_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    promo_start_date = models.DateField(null=True, blank=True)
    promo_end_date = models.DateField(null=True, blank=True)
    promo_discription = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


    def save(self, *args, **kwargs):
    # Check if the product doesn't already have a restaurant assigned
        if not self.restaurant_id:
            # Automatically set the restaurant based on the user's group
            if self.user.groups.filter(name='Restaurant').exists():
                restaurant = self.user.restaurant
                self.restaurant = restaurant
        super().save(*args, **kwargs)


class Orders(models.Model):
    STATUS =(
        ('Pending','Pending'),
        ('Order Confirmed','Order Confirmed'),
        ('Out for Delivery','Out for Delivery'),
        ('Delivered','Delivered'),
    )
    customer=models.ForeignKey('Customer', on_delete=models.CASCADE,null=True)
    product=models.ForeignKey('Product',on_delete=models.CASCADE,null=True)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, null=True)  # Add this field
    email = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=500,null=True)
    mobile = models.CharField(max_length=20,null=True)
    order_date= models.DateField(auto_now_add=True,null=True)
    status=models.CharField(max_length=50,null=True,choices=STATUS)


class Feedback(models.Model):
    name=models.CharField(max_length=40)
    feedback=models.CharField(max_length=500)
    date= models.DateField(auto_now_add=True,null=True)
    def __str__(self):
        return self.name
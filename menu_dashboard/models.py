from django.db import models
from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth.models import User, Group
from django.utils import timezone
from accounts.models import User  # Ensure this is the correct User model being imported
from django.conf import settings
from decimal import Decimal
from .qrcode_generator import generate_qrcode
from django.core.files import File


class Restaurant(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=40, null=True, blank=True)
    logo_pic = models.ImageField(upload_to='logo_pic/RestaurantLogo/', null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=20, null=False)

    @property
    def get_name(self):
        return self.restaurant_name

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return self.restaurant_name or "No Name"

    def get_total_orders(self):
        return Orders.objects.filter(restaurant=self).count()


def default_profile_pic():
    return 'media/default.jpg'  # Change this to the path of your default image


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/CustomerProfilePic/', default=default_profile_pic, null=True, blank=True)
    mobile = models.CharField(max_length=20, null=False)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return self.user.first_name or "No Name"


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
        return f"Table {self.table_number}" if self.table_number is not None else "No Table Number"


class Product(models.Model):
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    )
    name = models.CharField(max_length=40)
    product_image = models.ImageField(upload_to='product_image/', null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=200)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    subcategory = models.CharField(max_length=50, null=True, blank=True)
    pub_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    has_promo = models.BooleanField(default=False)
    promo_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    promo_start_date = models.DateField(null=True, blank=True)
    promo_end_date = models.DateField(null=True, blank=True)
    promo_discription = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name or "No Name"

    def save(self, *args, **kwargs):
        # Corrected indentation and logic for setting the restaurant
        if not self.restaurant_id:
            if self.user.groups.filter(name='Restaurant').exists():
                restaurant = self.user.restaurant
                self.restaurant = restaurant
        super().save(*args, **kwargs)


class Orders(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Order Confirmed', 'Order Confirmed'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
    )

    PAYMENT_METHOD = (
        ('Cash on Delivery', 'Cash on Delivery'),
        ('Credit Card', 'Credit Card'),
    )

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, null=True)
    order_date = models.DateField(auto_now_add=True, null=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS)
    payment_method = models.CharField(max_length=50, null=True, choices=PAYMENT_METHOD)
    table_number = models.IntegerField(null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        customer_name = f"{self.customer.user.first_name} {self.customer.user.last_name}" if self.customer else "No Customer"
        restaurant_name = self.restaurant.restaurant_name if self.restaurant else "No Restaurant"
        return f'Order {self.id} - Customer: {customer_name}, Restaurant: {restaurant_name}'


class OrderProduct(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of order

    def __str__(self):
        return f'Order {self.order_id} - Product: {self.product.name}, Quantity: {self.quantity}'


class Feedback(models.Model):
    name = models.CharField(max_length=40)
    feedback = models.CharField(max_length=500)
    date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name or "No Name"

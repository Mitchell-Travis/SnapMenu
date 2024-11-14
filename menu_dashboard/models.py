from django.db import models
from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth.models import User, Group
from django.utils import timezone
from accounts.models import User  # Ensure this is the correct User model being imported
from django.conf import settings
from decimal import Decimal
from .qrcode_generator import generate_qrcode
from django.core.files import File
from django.db.models import Index
from django.core.cache import cache
from django.utils.text import slugify

class Restaurant(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    slug = models.SlugField(max_length=40, unique=True, blank=True)
    logo_pic = models.ImageField(upload_to='logo_pic/RestaurantLogo/', null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=20, null=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    business_hours = models.CharField(max_length=255, null=True, blank=True)
    

    class Meta:
        indexes = [
            models.Index(fields=['restaurant_name']),
        ]

    def save(self, *args, **kwargs):
        if not self.restaurant_name_slug:
            self.restaurant_name_slug = slugify(self.restaurant_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.restaurant_name or "No Name"

    def get_total_orders(self):
        cache_key = f'restaurant_{self.id}_total_orders'
        total_orders = cache.get(cache_key)
        if total_orders is None:
            total_orders = Orders.objects.filter(restaurant=self).count()
            cache.set(cache_key, total_orders, timeout=3600)  # Cache for 1 hour
        return total_orders

def default_profile_pic():
    return 'media/default.jpg'

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/CustomerProfilePic/', default=default_profile_pic, null=True, blank=True)
    mobile = models.CharField(max_length=20, null=False)

    # Add a ForeignKey relationship to the Restaurant model
    restaurant = models.ForeignKey(Restaurant, null=True, blank=True, on_delete=models.SET_NULL)

    def assign_restaurant(self, restaurant):
        self.restaurant = restaurant
        self.save()

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return self.user.first_name or "No Name"


class Table(models.Model):
    table_number = models.IntegerField(null=True, blank=True, db_index=True)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='table', null=True, blank=True)
    qrcode_image = models.ImageField(upload_to='core/table_qrcodes', blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['restaurant', 'table_number']),
        ]

    def save(self, *args, **kwargs):
        if not self.qrcode_image:
            image_filename, image_buffer = generate_qrcode(self)
            self.qrcode_image.save(image_filename, File(image_buffer), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Table {self.table_number}" if self.table_number is not None else "No Table Number"

class Product(models.Model):
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    )
    name = models.CharField(max_length=40, db_index=True)
    product_image = models.ImageField(upload_to='product_image/', null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=200)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    subcategory = models.CharField(max_length=50, null=True, blank=True)
    pub_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available', db_index=True)
    has_promo = models.BooleanField(default=False)
    promo_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    promo_start_date = models.DateField(null=True, blank=True)
    promo_end_date = models.DateField(null=True, blank=True)
    promo_discription = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['restaurant', 'category', 'status']),
        ]

    def __str__(self):
        return self.name or "No Name"

    def save(self, *args, **kwargs):
        if not self.restaurant_id:
            if self.user.groups.filter(name='Restaurant').exists():
                restaurant = self.user.restaurant
                self.restaurant = restaurant
        super().save(*args, **kwargs)
        cache.delete(f'product_{self.id}')  # Invalidate cache on save

    @classmethod
    def get_product(cls, product_id):
        cache_key = f'product_{product_id}'
        product = cache.get(cache_key)
        if product is None:
            product = cls.objects.select_related('restaurant').get(id=product_id)
            cache.set(cache_key, product, timeout=3600)  # Cache for 1 hour
        return product

class Orders(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Order Confirmed', 'Order Confirmed'),
        ('Cooking', 'Cooking'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
    )

    PAYMENT_METHOD = (
        ('Cash on Delivery', 'Cash on Delivery'),
        ('Orange Money', 'Orange Money')
    )

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True, db_index=True)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, null=True, db_index=True)
    order_date = models.DateTimeField(auto_now_add=True, null=True, db_index=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS, default='Pending', db_index=True)
    payment_method = models.CharField(max_length=50, null=True, choices=PAYMENT_METHOD)
    table_number = models.IntegerField(null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['customer', 'restaurant', 'status', 'order_date']),
        ]

    def __str__(self):
        customer_name = f"{self.customer.user.first_name} {self.customer.user.last_name}" if self.customer else "No Customer"
        restaurant_name = self.restaurant.restaurant_name if self.restaurant else "No Restaurant"
        return f'Order {self.id} - Customer: {customer_name}, Restaurant: {restaurant_name}'

    def submit_delivery_request(self):
        from django.db import transaction
        with transaction.atomic():
            delivery_request = DeliveryRequest.objects.create(order=self)
            available_riders = Rider.objects.filter(is_available=True).select_for_update()
            if available_riders.exists():
                rider = available_riders.first()
                delivery_request.rider = rider
                delivery_request.status = 'Assigned'
                delivery_request.save()
                rider.is_available = False
                rider.save()
            else:
                delivery_request.status = 'No Riders Available'
                delivery_request.save()
        return delivery_request

class Rider(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20, null=False)
    is_available = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return self.user.username or "No Name"

class DeliveryRequest(models.Model):
    order = models.OneToOneField('Orders', on_delete=models.CASCADE)
    rider = models.ForeignKey('Rider', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, default='Pending', db_index=True)
    request_time = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['order', 'rider', 'status']),
        ]

    def __str__(self):
        return f'Delivery Request for Order {self.order.id}'

class Delivery(models.Model):
    delivery_request = models.OneToOneField('DeliveryRequest', on_delete=models.CASCADE)
    delivery_time = models.DateTimeField(null=True, blank=True, db_index=True)
    delivered = models.BooleanField(default=False, db_index=True)
    delivery_feedback = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['delivery_request', 'delivered']),
        ]

    def __str__(self):
        return f'Delivery for Order {self.delivery_request.order.id}'

class OrderProduct(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=['order', 'product']),
        ]

    def __str__(self):
        return f'Order {self.order_id} - Product: {self.product.name}, Quantity: {self.quantity}'

class Earnings(models.Model):
    order = models.OneToOneField('Orders', on_delete=models.CASCADE)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.51)
    currency = models.CharField(max_length=3, default='LRD')

    class Meta:
        indexes = [
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return f'Earnings from Order {self.order.id} - Service Charge: {self.service_charge} {self.currency}'

class UserCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True, db_index=True)

    def __str__(self):
        return f'{self.user.username} - {self.code}'

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f'{self.user.username} - Balance: {self.balance}'

class TopUpRequest(models.Model):
    user_code = models.ForeignKey(UserCode, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    processed = models.BooleanField(default=False, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['user_code', 'processed', 'timestamp']),
        ]

    def __str__(self):
        return f'{self.user_code.user.username} - Amount: {self.amount} - Processed: {self.processed}'

class Feedback(models.Model):
    name = models.CharField(max_length=40, db_index=True)
    feedback = models.CharField(max_length=500)
    date = models.DateField(auto_now_add=True, null=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['name', 'date']),
        ]

    def __str__(self):
        return self.name or "No Name"
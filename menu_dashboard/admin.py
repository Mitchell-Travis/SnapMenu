from django.contrib import admin
import qrcode
import zipfile
import io
from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
import qrcode
from io import BytesIO
from django.core.files import File
from django.contrib import admin
from .models import (
    Customer,
    Product,
    Orders,
    Feedback, 
    Table, 
    Restaurant, 
    )
from django.utils.html import format_html
from django.core.files.base import ContentFile
from django.utils.text import slugify


# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Customer, CustomerAdmin)


class RestaurantAdmin(admin.ModelAdmin):
    pass
admin.site.register(Restaurant, RestaurantAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'name')
admin.site.register(Product, ProductAdmin)

class OrderAdmin(admin.ModelAdmin):
    pass
admin.site.register(Orders, OrderAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    pass
admin.site.register(Feedback, FeedbackAdmin)
# Register your models here.


class TableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'view_qrcode')
    actions = ['download_qr_codes']

    def view_qrcode(self, obj):
        if obj.qrcode_image:
            qr_code_url = obj.qrcode_image.url
            return format_html('<a href="{}" target="_blank">View QR Code</a>', qr_code_url)
        return "No QR Code"

    view_qrcode.short_description = 'QR Code'

    def download_qr_codes(self, request, queryset):
        # Create a ZIP file to store the QR code images
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            base_url = "http://172.20.10.11:8000/"  # Replace with your desired base URL

            for table in queryset:
                if table.qrcode_image:
                    base_url = "http://172.20.10.11:8000/"  # Replace with your desired base URL
                    restaurant_name_slug = slugify(table.restaurant.restaurant_name)  # Slugify the name
                    table_qrcode_url = f'{base_url}/dashboard/{restaurant_name_slug}/{table.restaurant.id}'

                    # Generate the QR code image
                    qr = qrcode.QRCode(
                        version=None,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=15,
                        border=4,
                    )
                    qr.add_data(table_qrcode_url)
                    qr.make(fit=True)

                    # Create an image with a white QR code on a green background
                    qr_image = qr.make_image(fill_color="green", back_color="white")

                    # Save the image to a BytesIO buffer
                    image_buffer = BytesIO()
                    qr_image.save(image_buffer, format="PNG")

                    # Add the image to the ZIP file
                    image_filename = f"table_{table.table_number}.png"
                    zipf.writestr(image_filename, image_buffer.getvalue())

        # Build the response to send the ZIP file for download
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename=table_qr_codes.zip'
        return response

    download_qr_codes.short_description = 'Download QR Codes for Selected Tables'

admin.site.register(Table, TableAdmin)
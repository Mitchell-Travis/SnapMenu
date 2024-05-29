import qrcode
from qrcode.constants import ERROR_CORRECT_L
from django.utils.text import slugify
from io import BytesIO
from django.core.files import File

def generate_qrcode(table):
    if table.restaurant:
        base_url = "http://172.20.10.11:8000/"  # Replace with your desired base URL
        restaurant_name_slug = slugify(table.restaurant.restaurant_name)
        table_qrcode_url = f'{base_url}dashboard/{restaurant_name_slug}/{table.restaurant.id}'

        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_L,
            box_size=15,
            border=4,
        )
        qr.add_data(table_qrcode_url)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="green", back_color="white")

        image_buffer = BytesIO()
        qr_image.save(image_buffer, format="PNG")

        image_filename = f"table_{table.table_number}_qrcode.png"
        return image_filename, image_buffer
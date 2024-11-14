from django.shortcuts import render,redirect,reverse, get_object_or_404
from .models import *
from django.http import HttpResponseRedirect,HttpResponse, JsonResponse
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.conf import settings
from accounts.models import User
from datetime import datetime
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.http import HttpResponseServerError
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
from io import BytesIO
import json
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max
import logging
from weasyprint import HTML
from django.template.loader import render_to_string
from django.utils import timezone
import logging
# from django.db.models import Func, F
# from django.db.models.functions import Radians, Power, Sin, Cos, Sqrt, ATan2, Pi
# from django.contrib.gis.db.models.functions import Distance
# from django.contrib.gis.geos import Point



@login_required(login_url='vendor_login')
def vendor_topup(request):
    if request.method == 'POST':
        user_code = request.POST.get('user_code')
        amount = request.POST.get('amount')

        try:
            # Convert amount to Decimal
            amount = Decimal(amount)
            
            user_code_obj = UserCode.objects.get(code=user_code)
            user = user_code_obj.user
            wallet, created = Wallet.objects.get_or_create(user=user)

            topup_request = TopUpRequest.objects.create(
                user_code=user_code_obj,
                amount=amount  # Use Decimal amount
            )
            wallet.balance += amount  # Use Decimal amount
            wallet.save()
            topup_request.processed = True
            topup_request.save()

            return JsonResponse({'message': 'Top-up successful', 'new_balance': wallet.balance})
        except UserCode.DoesNotExist:
            return JsonResponse({'message': 'Invalid user code'}, status=400)
        except Exception as e:
            return JsonResponse({'message': f'Error: {str(e)}'}, status=500)

    return render(request, 'menu_dashboard/vendor_topup.html')


@login_required
def view_wallet(request):
    user = request.user
    wallet, created = Wallet.objects.get_or_create(user=user)
    topup_requests = TopUpRequest.objects.filter(user_code__user=user).order_by('-timestamp')
    
    print(f"Wallet Balance: {wallet.balance}")  # Debug print
    print(f"Top-up Requests: {topup_requests}")  # Debug print

    return render(request, 'menu_dashboard/view_wallet.html', {
        'wallet': wallet,
        'topup_requests': topup_requests
    })

def delete_product(request, product_id):
    try:
        # Perform the deletion logic here based on the product_id
        product = Product.objects.get(pk=product_id)
        product.delete()
        return JsonResponse({'message': 'Product deleted successfully'})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)


@login_required(login_url='adminlogin')
def restaurant_menu_list(request):
    current_user = request.user
    restaurant = Restaurant.objects.get(user=request.user)

    # Filter products by the restaurant
    products = Product.objects.filter(restaurant=current_user.restaurant)
    product_count = Product.objects.filter(restaurant=current_user.restaurant).count()


    context = {
        'products': products,
        'product_count': product_count
    }
    return render(request, 'menu_dashboard/products.html', context)


def contact(request):

    context = {

    }

    return render(request, 'menu_dashboard/contact.html', context)


def restaurant_menu(request, restaurant_id, restaurant_name_slug):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    products = Product.objects.filter(restaurant=restaurant)

    allProds = []
    beverages = []

    categories = set(products.values_list('category', flat=True))
    for category in categories:
        if category == 'Drinks':
            beverages = products.filter(category=category)
        else:
            prod = products.filter(category=category)[:6]
            if prod:
                allProds.append(prod)

    context = {
        'restaurant': restaurant,
        'allProds': allProds,
        'beverages': beverages,
    }

    return render(request, 'menu_dashboard/index.html', context)




logger = logging.getLogger(__name__)

@login_required(login_url='customer_signin')
def order_success(request, order_id):
    # Fetch the order
    order = get_object_or_404(Orders, id=order_id)

    # Ensure the user is authorized to view this order
    if request.user.customer != order.customer:
        return HttpResponseForbidden("You are not authorized to view this order.")

    # Fetch the restaurant
    restaurant = get_object_or_404(Restaurant, id=order.restaurant.id)
    restaurant_slug = restaurant.slug  # Make sure this field exists and is not empty

     # Clear the cart
    if 'cart' in request.session:
        del request.session['cart']

    # Prepare context
    context = {
        'restaurant_name_slug': restaurant_slug,  # Pass the slug to the template
        'restaurant_id': restaurant.id,           # Pass the restaurant ID to the template
        'restaurant_name': restaurant.restaurant_name,  # For display
        'order_id': order.id,
        'order_time': order.order_date,
        'payment_method': order.payment_method,
        'customer_name': f"{order.customer.user.first_name} {order.customer.user.last_name}",
        'table_number': order.table_number,
        'amount': order.amount,
    }

    return render(request, 'menu_dashboard/order_success.html', context)




@login_required(login_url='customer_signin')
def download_receipt(request, order_id):
    try:
        order = get_object_or_404(Orders, id=order_id)

        # Check authorization
        if request.user.customer != order.customer:
            logger.warning(f"Unauthorized receipt access attempt for order {order_id} by user {request.user.id}")
            return render(request, 'menu_dashboard/unauthorized.html', status=403)

        # Prepare context
        context = {
            'order': order,
            'customer_name': f"{order.customer.user.get_full_name()}",
            'order_time': order.order_date,
            'generated_at': timezone.now()
        }

        # Generate PDF
        html_string = render_to_string('menu_dashboard/receipt_template.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf()

        # Prepare response
        filename = f"receipt_{order.id}_{timezone.now().strftime('%Y%m%d')}.pdf"
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f"Receipt generated for order {order_id}")
        return response

    except Exception as e:
        logger.error(f"Error generating receipt for order {order_id}: {str(e)}")
        return render(request, 'menu_dashboard/error.html', {'error': 'Failed to generate receipt'}, status=500)

    

def restaurant_search(request):
    query = request.GET.get('q')
    if query:
        restaurants = Restaurant.objects.filter(restaurant_name__icontains=query)
    else:
        restaurants = Restaurant.objects.all()

    context = {
        'restaurants': restaurants,
        'query': query,
    }

    return render(request, 'menu_dashboard/store-list.html', context)




def restaurant_list(request):
    # Fetch all restaurants from the database
    restaurants = Restaurant.objects.all()

    context = {
        'restaurants': restaurants,
    }

    return render(request, 'menu_dashboard/store-list.html', context)


import logging

logger = logging.getLogger(__name__)

@login_required(login_url='customer_signin')
def restaurant_checkout(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == 'POST':
        try:
            cart_data = request.POST.get('cart')

            if not cart_data:
                return JsonResponse({'message': 'Cart data is missing'}, status=400)

            cart = json.loads(cart_data)
            payment_method = request.POST.get('payment_method')

            # Ensure the customer exists
            customer, created = Customer.objects.get_or_create(user=request.user)

            # Fetch the first available table, if any
            table = Table.objects.filter(restaurant=restaurant).first()
            table_number = table.table_number if table else None

            # Create the order
            order = Orders.objects.create(
                customer=customer,
                restaurant=restaurant,
                status='Pending',
                payment_method=payment_method,
                table_number=table_number,
                amount=0
            )

            total_amount = Decimal('0.00')
            service_charge = Decimal('0.51')

            # Process each item in the cart
            for product_id, item_data in cart.items():
                product = get_object_or_404(Product, id=product_id)
                quantity = item_data[0]
                amount = product.price * quantity
                total_amount += amount

                OrderProduct.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

            total_amount += service_charge
            order.amount = total_amount
            order.save()

            # Record earnings
            Earnings.objects.create(order=order, service_charge=service_charge)

            # Log the order creation
            logger.info(f"Order placed successfully: Order ID {order.id}")

            # Optionally clear the cart here
            request.session.pop('cart', None)

            return JsonResponse({'message': 'Order placed successfully', 'order_id': order.id, 'total_amount': str(total_amount)})

        except Exception as e:
            logger.error(f"Error processing order: {e}")
            return JsonResponse({'message': f"Error processing order. Please try again. {str(e)}"}, status=500)

    return render(request, 'menu_dashboard/checkout.html', {'restaurant': restaurant, 'restaurant_id': restaurant_id})





@login_required(login_url='adminlogin')
def create_restaurant_menu(request):

    current_user = request.user
    restaurant = Restaurant.objects.get(user=request.user)

    if request.method == 'POST':
        # Retrieve form data for the product
        name = request.POST['name']
        product_image = request.FILES.get('product_image')  # Use get() to handle missing image gracefully
        price = request.POST['price']
        description = request.POST['description']
        category = request.POST['category']  # Retrieve the selected category

        # Retrieve promo form fields
        has_promo = request.POST.get('has_promo') == 'on'  # Check if the checkbox is checked
        promo_price = request.POST.get('promo_price')
        promo_start_date = request.POST.get('promo_start_date')
        promo_end_date = request.POST.get('promo_end_date')
        promo_discription = request.POST.get('promo_discription')

        # Retrieve form data for the table
        table_number = request.POST.get('table_number')

        try:
            # Validate that price is a valid decimal number
            price_decimal = Decimal(price)

            # Create a new product
            product = Product(
                name=name,
                product_image=product_image,
                price=price_decimal,
                description=description,
                category=category,  # Assign the selected category directly
                pub_date=datetime.now(),
                restaurant=request.user.restaurant,
                has_promo=has_promo,
                promo_price=promo_price,
                promo_start_date=promo_start_date,
                promo_end_date=promo_end_date,
                promo_discription=promo_discription
            )

            # Validate the model fields
            product.full_clean()

            # Save the product to the database
            product.save()

            # Create a new table if the table_number is provided
            if table_number:
                table = Table(
                    table_number=table_number,
                    restaurant=request.user.restaurant
                )
                table.full_clean()
                table.save()

            messages.success(request, 'Product created successfully.')
            return redirect('restaurant-menu-list')  # Redirect to a product listing page

        except ValidationError as e:
            for error in e:
                messages.error(request, error)

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    context = {
        # Pass any additional context data needed
    }

    return render(request, 'menu_dashboard/add-product.html', context)
    



@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    current_user = request.user
    restaurant = Restaurant.objects.get(user=request.user)

    total_orders = restaurant.get_total_orders()

    product_count = Product.objects.filter(restaurant=current_user.restaurant).count()

    # Generate the menu URL based on the restaurant's unique identifier and slugified name
    restaurant_id = restaurant.id
    restaurant_name = restaurant.restaurant_name
    restaurant_name_slug = slugify(restaurant_name)  # Slugify the name

    # Get the logo image URL
    logo_image_url = restaurant.logo_pic.url  # Assuming you have a logo_pic field in your Restaurant model

    restaurant_menu = reverse('restaurant_menu', args=[restaurant_name_slug, restaurant_id])

    context = {
        'product_count': product_count,
        'total_orders': total_orders,
        'restaurant_menu': restaurant_menu,
        'restaurant_name': restaurant_name,
        'logo_image_url': logo_image_url,  # Add the logo image URL to the context
    }

    return render(request, 'menu_dashboard/dashboard_view.html', context)

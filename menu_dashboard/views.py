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
    # Get the specific restaurant using the provided restaurant_id
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Fetch all products associated with the restaurant, grouped by category
    products = Product.objects.filter(restaurant=restaurant)
    categories = set(products.values_list('category', flat=True))
    
    allProds = []
    for category in categories:
        prod = products.filter(category=category)[:6]  # Limit to 6 products per category
        if prod:
            allProds.append(prod)

    context = {
        'restaurant': restaurant,
        'allProds': allProds,
    }

    return render(request, 'menu_dashboard/index.html', context)



def restaurant_category_menu(request):

    context = {


    }


    return render(request, 'menu_dashboard/index-2.html', context)



@login_required(login_url='customer_signin')
def restaurant_checkout(request, restaurant_id):
    if request.method == 'POST':
        try:
            cart = request.POST.get('cart')
            cart = json.loads(cart)  # Parse the JSON cart data

            customer = request.user.customer  # Get the logged-in customer

            for product_id, item_data in cart.items():
                quantity = item_data[0]
                product = Product.objects.get(id=product_id)
                restaurant = product.restaurant  # Assuming the Product model has a ForeignKey to Restaurant

                for _ in range(quantity):
                    Orders.objects.create(
                        customer=customer,
                        product=product,
                        restaurant=restaurant,
                        status='Pending'
                    )

            # Return a JSON response indicating success
            return JsonResponse({'message': 'Order placed successfully'})

        except Exception as e:
            # Log the error
            print(f"Error processing order: {e}")
            # Return an error response
            return JsonResponse({'message': 'Error processing order. Please try again.'}, status=500)

    # Get the restaurant based on the restaurant ID
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Render the checkout page
    return render(request, 'menu_dashboard/shop-checkout.html', {'restaurant': restaurant})



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
        category_id = request.POST['category']  # Retrieve the selected category ID

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

            # Retrieve the selected category
            category = Category.objects.get(id=category_id)

            # Create a new product
            product = Product(
                name=name,
                product_image=product_image,
                price=price_decimal,
                description=description,
                category=category,  # Assign the selected category
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

    # Get the logo image URL
    logo_image_url = restaurant.logo_pic.url

    # Fetch categories for populating the dropdown
    categories = Category.objects.all()

    context = {
        'categories': categories,
        'logo_image_url ':logo_image_url
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

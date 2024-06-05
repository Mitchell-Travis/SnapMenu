from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect
from django.contrib import messages
from menu_dashboard.models import Restaurant, Customer  # Import your Restaurant model
from django.core.files.storage import FileSystemStorage  # Import FileSystemStorage if not already imported

from accounts.models import User, VerifyConfirmation, ConfirmationCode
from accounts.send_email_confirmation import EmailConfirmation
from django.urls import reverse
from django.contrib.auth.decorators import login_required



def is_restaurant_owner(user):
    return user.groups.filter(name='Restaurant').exists()

def is_customer(user):
    return user.groups.filter(nmae='Customer').exists()


def afterlogin_view(request):
    if is_restaurant_owner(request.user):
        return redirect('admin-dashboard')
    else:
        return redirect('home')


def after_customer_login(request):
    if is_customer(request.user):
        return redirect('customer-dashboard')

    else:
        return redirect('home')


def signup_view(request):
    if request.method == 'POST':
        # Retrieve form data from request.POST
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Create a CustomUser instance and set its attributes
        user = User.objects.create_user(username=username, email=email, password=password)

        # Add the user to the 'Restaurant' group
        my_restaurant_group, created = Group.objects.get_or_create(name='Restaurant')
        my_restaurant_group.user_set.add(user)

        # Authenticate the user with email and password
        user = authenticate(email=email, password=password)

        if user is not None and user.is_active:
            # Log the user in
            login(request, user)

            # Redirect to the restaurant creation page
            return redirect('restaurant_profile')

    return render(request, 'accounts/signup.html')


def customer_signup_view(request):
    if request.method == 'POST':
        # Retrieve form data from request.POST
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Create a User instance and set its attributes
        user = User.objects.create_user(username=username, email=email, password=password)

        # Add the user to the 'Customer' group
        customer_group, created = Group.objects.get_or_create(name='Customer')
        user.groups.add(customer_group)

        # Create a Customer instance and associate it with the user
        customer = Customer.objects.create(user=user)

        # Authenticate the user with email and password
        user = authenticate(email=email, password=password)

        if user is not None and user.is_active:
            # Log the user in
            login(request, user)

            # Redirect to a specific customer profile page or home page
            return redirect('customer_profile')

    return render(request, 'accounts/customer_signup.html')



def customer_signin_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(email=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                # Check if the user is a member of the 'Customer' group
                if user.groups.filter(name='Customer').exists():
                    # Get the associated restaurant for the user
                    try:
                        # Ensure that the user has a customer profile
                        customer = user.customer
                        
                        if customer:
                            # Assuming there's a ForeignKey from Customer to Restaurant
                            restaurant = customer.restaurant
                            if restaurant:
                                # Redirect to the restaurant checkout page
                                return redirect('restaurant_checkout', restaurant_id=restaurant.id)
                            else:
                                # Handle case where customer is not associated with any restaurant
                                messages.error(request, 'No restaurant associated with this customer')
                                return redirect('home')  # Redirect to home page or another appropriate page
                        else:
                            # Handle case where user has no customer profile
                            messages.error(request, 'Customer profile not found')
                            return redirect('home')  # Redirect to home page or another appropriate page

                    except AttributeError:
                        # Handle case where user has no customer profile
                        messages.error(request, 'Customer profile not found')
                        return redirect('home')  # Redirect to home page or another appropriate page
                    except Restaurant.DoesNotExist:
                        # Handle case where associated restaurant does not exist
                        messages.error(request, 'Associated restaurant does not exist')
                        return redirect('home')  # Redirect to home page or another appropriate page
                else:
                    # Handle other user types or roles here
                    return redirect('home')

            else:
                messages.error(request, 'Your account has been disabled')
        else:
            # Add validation errors for both email and password
            messages.error(request, 'Invalid login credentials')
            if not email:
                messages.error(request, 'Email is required')
            if not password:
                messages.error(request, 'Password is required')

    return render(request, 'accounts/customer_signin.html')




def create_restaurant_profile(request):
    if request.method == 'POST':
        # Retrieve form data from request.POST
        restaurant_name = request.POST.get('restaurant_name')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        # Handle file upload
        uploaded_file = request.FILES['logo_pic']  # Update the field name to match your form
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)

        # Get the currently logged-in user (the one created in step 1)
        user = request.user

        # Create a Restaurant instance and set its attributes
        restaurant = Restaurant.objects.create(
            user=user,  # Associate the restaurant with the user
            restaurant_name=restaurant_name,
            logo_pic=filename,
            address=address,
            mobile=mobile
        )

        # Send email confirmation code to user
        EmailConfirmation(request, user.username, user.email, user.password)  # You might need to adjust this part based on your email handling

        return render(request, 'accounts/email-verification-message.html')

    return render(request, 'accounts/create_restaurant_profile.html')



@login_required
def create_customer_profile(request):
    if request.method == 'POST':
        # Retrieve form data from request.POST
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mobile = request.POST.get('mobile')

        # Handle file upload for profile picture (if applicable)
        if 'profile_pic' in request.FILES:
            uploaded_file = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
        else:
            # If no profile picture is uploaded, set filename to None or provide a default image path
            filename = None  # Or provide the default image path here

        # Get the logged-in user
        user = request.user

        # Update the user's first and last name
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Check if the customer profile already exists
        customer, created = Customer.objects.get_or_create(user=user, defaults={'mobile': mobile, 'profile_pic': filename})

        if not created:
            # Update the existing customer profile
            customer.mobile = mobile
            if filename:
                customer.profile_pic = filename
            customer.save()

        # Redirect to a success page or perform any other action
        return redirect('customer_signin')

    return render(request, 'accounts/customer_profile.html')


def signin_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password'] 

        user = authenticate(email=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Check if the user is a member of the 'Restaurant' group
                if user.groups.filter(name='Restaurant').exists():
                    return redirect('admin-dashboard')
                else:
                    # Handle other user types or roles here
                    return redirect('home')

            else:
                messages.error(request, 'Your account has been disabled')
        else:
            # Add validation errors for both email and password
            messages.error(request, 'Invalid login credentials')
            if not email:
                messages.error(request, 'Email is required')
            if not password:
                messages.error(request, 'Password is required')

    return render(request, 'accounts/signin.html')


def Logout(request):
    logout(request)
    return redirect('home')


def verify_restaurant_account(request):
    if request.method == 'POST':
        # Get the entered verification code from request.POST
        verified_code = request.POST.get('verified_code')

        # Get the confirmation code that has been sent
        config_code = ConfirmationCode.objects.filter(user=request.user).first()

        # Check if the entered code matches the sent code
        if verified_code == config_code.confirmed_code:
            # Create or update the VerifyConfirmation instance
            verify_confirmation, created = VerifyConfirmation.objects.get_or_create(user=request.user)
            verify_confirmation.verified_code = verified_code
            verify_confirmation.save()

            # Redirect to a success page or do whatever you want
            return render(request, 'accounts/verification_pass.html', {'verified_code': verified_code})
        else:
            return render(request, 'accounts/verify_account.html', {'error_message': 'Verification failed. Please check your email to verify the code'})

    return render(request, 'accounts/verification.html')







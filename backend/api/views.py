from django.shortcuts import render, redirect, get_object_or_404
from .models import Review, UserProfile, Restaurant, Dish, Cart, CartItem, OrderItem
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Order
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import logging

# Create a logger
logger = logging.getLogger(__name__)

def base(response):
    return render(response, 'base.html')

def home(request):
    # Retrieve all restaurants from the database
    restaurants = Restaurant.objects.all()
    return render(request, 'home.html', {'restaurants': restaurants})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Attempt to authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page if login is successful
        else:
            # If authentication fails, display an error message
            messages.error(request, 'Invalid username or password')
            return redirect('login')  # Redirect back to the login page with the error message

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home') 


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        user_type = request.POST['user_type']
        restaurant_name = request.POST.get('restaurant_name', None)
        location = request.POST.get('location', None)
        restaurant_photo = request.FILES.get('restaurant_photo', None)  # Handling restaurant photo upload

        # Check if passwords match
        if password != password_confirm:
            return render(request, 'register.html', {'error': "Passwords do not match."})

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create the user profile
        user_profile = UserProfile.objects.create(
            user=user,
            user_type=user_type,
            restaurant_name=restaurant_name if user_type == 'restaurant' else None,
            location=location if user_type == 'restaurant' else None,
        )

        # If the user is a restaurant, create the restaurant and link the restaurant photo
        if user_type == 'restaurant':
            # Create the restaurant and associate it with the user
            restaurant = Restaurant.objects.create(
                name=restaurant_name,
                owner=user,  # Assuming 'owner' is a OneToOneField to the user
                address=location,
            )

            # Optionally, save the restaurant photo
            if restaurant_photo:
                restaurant.photo = restaurant_photo
                restaurant.save()

            # Link the restaurant to the user profile
            user_profile.restaurant = restaurant
            user_profile.save()

        # Authenticate and log in the user
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page after successful registration

    return render(request, 'register.html')

@login_required
def profile(request):
    profile = request.user.profile
    return render(request, 'profile.html', {'profile': profile})

def post_review(request):
    if request.method == 'POST':
        # Get data from the form
        restaurant = request.POST.get('restaurant')
        rating = request.POST.get('rating')
        note = request.POST.get('note')

        # Create a new review object
        review = Review.objects.create(
            restaurant=restaurant,
            rating=rating,
            note=note
        )

        messages.success(request, 'Review posted successfully!')

        # Redirect to the reviews page after posting the review
        return redirect('reviews')  # 'reviews' is the URL name for your review page
    
    # If the method is not POST, render the form
    return render(request, 'reviews.html')

def reviews(request):
    reviews = Review.objects.all()
    
    # Prepare a list of star counts for each review based on its rating
    for review in reviews:
        review.full_stars = range(1, review.rating + 1)  # List of filled stars (1 to rating)
        review.empty_stars = range(review.rating + 1, 6)  # List of empty stars (rating+1 to 5)
    
    return render(request, 'reviews.html', {'reviews': reviews})

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    total_price = sum(item.dish.price * item.quantity for item in cart_items)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})



@login_required
def manage_order(request):
    if not hasattr(request.user, 'restaurant'):  # Ensure user is a restaurant owner
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        action = request.POST.get("action")
        
        try:
            order = Order.objects.get(id=order_id, restaurant=request.user.restaurant)
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect('manage_orders')
        
        if action == "approve":
            order.status = "approved"  # Set status to approved
            order.save()
            messages.success(request, "Order approved successfully.")
        elif action == "deny":
            order.status = "denied"  # Set status to denied
            order.save()
            messages.success(request, "Order denied successfully.")
        else:
            messages.error(request, "Invalid action.")
        
        return redirect('manage_order')

    # Fetch orders for the logged-in restaurant owner
    orders = Order.objects.filter(restaurant=request.user.restaurant).order_by('-created_at')
    return render(request, 'manage_orders.html', {'orders': orders})


@login_required
def add_dish(request):
    if request.method == 'POST':
        try:
            # Collect the form data
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            photo = request.FILES.get('photo')  # Handle the uploaded file

            # Check if all required fields are provided
            if not all([name, price, photo]):
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            # Get the restaurant associated with the logged-in user
            # Ensure the user has a restaurant
            try:
                restaurant = request.user.restaurant
            except Restaurant.DoesNotExist:
                return JsonResponse({'error': 'You must be associated with a restaurant to add a dish.'}, status=400)

            # Create a new Dish instance
            dish = Dish.objects.create(
                name=name,
                description=description,
                price=price,
                photo=photo,
                restaurant=restaurant,  # Assign the restaurant
            )

            # Return a success response
            return JsonResponse({'message': 'Dish added successfully.'}, status=201)

        except Exception as e:
            # Log the error and send a generic error message to the user
            logger.error(f"Error adding dish: {e}")
            return JsonResponse({'error': 'Internal server error. Please try again later.'}, status=500)

    # Render the add_dish.html template when the request method is GET
    return render(request, 'add_dish.html')

@login_required
def add_to_cart(request, dish_id):
    """Add a dish to the user's cart."""
    dish = get_object_or_404(Dish, id=dish_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the dish is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, dish=dish)
    if not created:
        cart_item.quantity += 1
    cart_item.save()

    messages.success(request, f"{dish.name} added to your cart!")
    return redirect('restaurant_detail', restaurant_id=dish.restaurant.id)

def restaurant_detail(request, restaurant_id):
    """Display all dishes for a specific restaurant."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    dishes = restaurant.menu.all()  # This should fetch dishes related to the restaurant.
    return render(request, 'restaurant_detail.html', {'restaurant': restaurant, 'dishes': dishes})

def view_dishes(request):
    # Get the logged-in user's profile
    user_profile = request.user.profile
    
    # If the user is a restaurant, get the dishes for that restaurant
    if user_profile.user_type == 'restaurant':
        # Get dishes associated with the restaurant
        dishes = Dish.objects.filter(restaurant=user_profile.restaurant)
        return render(request, 'view_dishes.html', {'dishes': dishes})

    return render(request, 'error.html', {'message': 'You are not authorized to view dishes.'})

@login_required
def proceed_to_checkout(request):
    # Get the user's cart
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect('cart')

    # Calculate total price
    total_price = sum(item.dish.price * item.quantity for item in cart.items.all())

    # Create the order
    restaurant = cart.items.first().dish.restaurant  # Assuming all items are from one restaurant
    order = Order.objects.create(
        customer=request.user,
        restaurant=restaurant,
        total_price=total_price,
    )

    # Add items to the order
    for item in cart.items.all():
        OrderItem.objects.create(order=order, dish=item.dish, quantity=item.quantity)

    # Clear the cart
    cart.items.all().delete()

    # Return a JSON response for the alert
    return JsonResponse({'message': 'Waiting for approval'}, status=200)


@login_required
def order_status(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'order_status.html', {'orders': orders})
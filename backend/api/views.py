from django.shortcuts import render, redirect
from .models import Review
from django.contrib import messages

def base(response):
    return render(response, 'base.html')

def home(request):
    return render(request, 'home.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def reviews(request):
    return render(request, 'reviews.html')

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


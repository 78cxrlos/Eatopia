from django.db import models
from django.contrib.auth.models import User

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant')  # Link restaurant to user
    address = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to='restaurant_photos/', null=True, blank=True)  # Optional restaurant photo

    def __str__(self):
        return self.name
class UserProfile(models.Model):
    USER_TYPES = (
        ('normal', 'Normal User'),
        ('restaurant', 'Restaurant'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='normal')
    restaurant_name = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    photo = models.ImageField(upload_to='restaurant_photos/', blank=True, null=True)  # New field for photo
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, null=True, blank=True)  # Link to the restaurant

    def __str__(self):
        return self.user.username
    
class Review(models.Model):
    restaurant = models.CharField(max_length=100)
    rating = models.PositiveIntegerField()
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.restaurant} - {self.rating} stars"

# Dish model
class Dish(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to='dish_photos/', blank=True, null=True)  # Use ImageField
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu')

    def __str__(self):
        return self.name

# Cart model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    
    def __str__(self):
        return f"Cart of {self.user.username}"

# Cart Item model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"

# Order model
class Order(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    DENIED = 'denied'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DENIED, 'Denied')
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} for {self.restaurant.name}"

# OrderItem model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"


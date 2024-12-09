from django.db import models

class Review(models.Model):
    restaurant = models.CharField(max_length=100)
    rating = models.PositiveIntegerField()
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.restaurant} - {self.rating} stars"

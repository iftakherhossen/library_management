from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    author = models.CharField(max_length=100, blank=True, null=True,)
    description = models.TextField()
    image = models.ImageField(upload_to='books/images/', blank=True, null=True)
    borrowing_price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey(Category, related_name='books', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    comment = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review by {self.name}"
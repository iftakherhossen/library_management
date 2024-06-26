from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from django.views import View
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Category, Book
from .forms import ReviewForm

# Create your views here.
class LibraryBooksView(View):
    template_name = 'books/library_books.html'
    
    def get(self, request, category_slug=None):
        categories = Category.objects.all().order_by('name')
        
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            books = Book.objects.filter(category=category).order_by('title')
            book_count = books.count()
            filtered = True
            categorySlug = category.name
        else:
            books = Book.objects.all().order_by('title')
            book_count = books.count()
            filtered = False
            categorySlug = ''
                  
        return render(request, self.template_name, {'books': books, 'categories': categories, 'book_count': book_count, 'filtered': filtered, 'categorySlug': categorySlug})
    
class BookDetailsView (DetailView):
    model = Book
    slug_url_kwarg = 'book_slug'
    template_name = 'books/view_book.html'
    
    def post(self, request, *args, **kwargs):
        review_form = ReviewForm(data=self.request.POST)
        book = self.get_object()
        
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.book = book
            new_review.save()
            return HttpResponseRedirect(reverse('view_book', kwargs={'book_slug': book.slug}))
            
        return self.get(request, *args, **kwargs)
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        book = self.object
        reviews = book.reviews.all().order_by('-id')        
        review_form = ReviewForm()
                
        context['user'] = self.request.user
        context['reviews'] = reviews
        context['review_form'] = review_form
        return context
    
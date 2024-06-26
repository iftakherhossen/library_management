from django.urls import path
from .views import LibraryBooksView, BookDetailsView
from transactions.views import BorrowBookView, ReturnBookView

urlpatterns = [
    path('', LibraryBooksView.as_view(), name='books'),
    path('category/<slug:category_slug>/', LibraryBooksView.as_view(), name='categorizedBooks'),
    path('<slug:book_slug>/', BookDetailsView.as_view(), name='view_book'),
    path('<slug:book_slug>/borrow/', BorrowBookView.as_view(), name='borrow'),
    path('<slug:book_slug>/return/<int:transaction_id>', ReturnBookView.as_view(), name='return'),
]
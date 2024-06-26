from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserLogOutView, UserAccountView, UserAccountUpdateView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogOutView.as_view(), name='logout'),
    path('profile/', UserAccountView.as_view(), name='profile'),
    path('edit-profile/', UserAccountUpdateView.as_view(), name='edit_profile'),
]
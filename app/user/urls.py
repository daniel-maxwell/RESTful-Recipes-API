"""
URL mapping for the User API.
"""

from django.urls import path

from user import views

app_name = 'user'

# Set the URL patterns for the User API
urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManagerUserView.as_view(), name='me'),
]

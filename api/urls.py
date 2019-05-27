from django.urls import path
from .views import  *

urlpatterns = [
    path('search' , SearchView.as_view() , name = "search"),
    path('cart' , AddCart.as_view() , name = "cart"),
    path('checkout' , CheckOut.as_view() , name = "checkout"),
]
from django.urls import path
from .views import  *

urlpatterns = [
	
	path('' , Home.as_view() , name = 'home'),
    path('search' , SearchView.as_view() , name = "search"),
    path('checkout' , CheckOut.as_view() , name = "checkout"),
]
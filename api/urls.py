from django.urls import path
from .views import  *

urlpatterns = [	
	path('Category' , Category.as_view() , name = 'category'),
    path('search' , SearchView.as_view() , name = "search"),
    path('checkout' , CheckOut.as_view() , name = "checkout"),
    path('product' , Product.as_view() , name = "product"),
]
from django.urls import path
from .views import  *
from api import views

urlpatterns = [	
	path('home' , Home.as_view() , name = 'home'),
    path('search' , SearchView.as_view() , name = "search"),
    path('checkout' , CheckOut.as_view() , name = "checkout"),
    path('checkoutpage' , views.checkoutpage , name = "checkoutpage"),
    path('product' , Product.as_view() , name = "product"),
    path('vehicle/information' , VehicleInfo.as_view() , name = "vehicle_info"),
    path('leaseterm' , LeaseTerms.as_view() , name = "leaseterm"),
    path('order', Orders.as_view(), name = "order")
]
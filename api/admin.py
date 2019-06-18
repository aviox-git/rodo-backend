from django.contrib import admin
from .models import *

class CategoryAdmin(admin.ModelAdmin):

	prepopulated_fields  = {"slug": ("name",),}

# Register your models here.

admin.site.register(Profile)
admin.site.register(Year)
admin.site.register(Make)
admin.site.register(Model)
admin.site.register(Trim)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductDetail)
admin.site.register(Coupon)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(MetaContent)
admin.site.register(LeaseTerm)
admin.site.register(VehicleInformation)







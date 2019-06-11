from django.db import models
import uuid
from django.utils.timezone import now
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.core.exceptions import ValidationError


# Create your models here.

class Profile(models.Model):
	email = models.EmailField()
	phone = models.BigIntegerField(null = True , blank = True)

	def __str__(self):
		return self.email

class Year(models.Model):
	year = models.PositiveSmallIntegerField()

	def __str__(self):
		return str(self.year)

class Make(models.Model):
	make = models.CharField(max_length = 100, db_index=True,)
	year = models.ForeignKey(Year , on_delete = models.CASCADE, related_name = "yearsname")

	def __str__(self):
		return self.make + " | " + str(self.year.year)

class Model(models.Model):
	model = models.CharField(max_length = 100, db_index=True,)
	make = models.ForeignKey(Make, on_delete = models.CASCADE , related_name = "makename")

	def __str__(self):
		return  self.make.make + " " + self.model

class Trim(models.Model):
	trim = models.CharField(max_length = 100, db_index=True) 
	model = models.ForeignKey(Model, on_delete = models.CASCADE, related_name = "modelsname")

	def __str__(self):
		return self.model.make.make + " - " + self.model.model + " - " + self.trim

class Category(models.Model):
	name = models.CharField(max_length = 100)
	description = models.TextField(null = True)
	image = models.ImageField(upload_to = "category")

	def __str__(self):
		return self.name


class ProductDetail(models.Model):
	trim  = models.ForeignKey(Trim , on_delete = models.CASCADE)
	category = models.ForeignKey(Category , on_delete = models.CASCADE, related_name = "categories")
	price = models.IntegerField()
	description = RichTextUploadingField(null = True)
	more_description = RichTextUploadingField(null = True)
	image = models.ImageField(upload_to = "products" , null = True)

	def __str__(self):
		return self.trim.model.make.make + " " + self.trim.model.model + " " + self.trim.trim + " with price - " +  str(self.price) + " in Category " + self.category.name

class Coupon(models.Model):
	name = models.CharField(max_length = 200)

	def __str__(self):
		return self.name

class Order(models.Model):
	orderId = models.UUIDField(default=uuid.uuid4,editable=False)
	totalPrice = models.IntegerField()
	finalPrice = models.IntegerField()
	status = models.BooleanField(default = False)
	date = models.DateTimeField(default=now, editable=False)
	coupon = models.ForeignKey(Coupon , on_delete = models.CASCADE, null = True, blank = True)
	profile = models.ForeignKey(Profile , on_delete = models.CASCADE, null = True, blank = True)

	def __str__(self):
		return str(self.orderId) + " | " + str(self.finalPrice) 

class OrderItem(models.Model):
	order = models.ForeignKey(Order , on_delete = models.CASCADE)
	product = models.ForeignKey(ProductDetail , on_delete = models.CASCADE, null=True)
	transaction_id = models.CharField(max_length = 100, null =  True)

	def __str__(self):
		return str(self.order.orderId) + " | " #+ self.product.trim.trim

# class CardDetail(models.Model):
# 	card_number = models.BigIntegerField()
# 	expiry_date = models.DateField()
# 	cvc = models.PositiveSmallIntegerField()
# 	profile = models.ForeignKey(Profile , on_delete = models.CASCADE)

# 	def __str__(self):
# 		return self.profile.email + " | " + self.cvc

class Address(models.Model):
	profile = models.ForeignKey(Profile , on_delete = models.CASCADE)
	first_name = models.CharField(max_length = 200)
	last_name = models.CharField(max_length = 200)
	address = models.TextField()
	state = models.CharField(max_length = 200, null = True, blank = True)
	city = models.CharField(max_length = 200, null = True, blank = True)
	zipcode = models.CharField(max_length = 200, null = True, blank = True)

	def __str__(self):
		return ("{} {} {}").format(self.first_name, self.last_name, self.profile.email)


class MetaContent(models.Model):
	page_choices = (("home", "Home"), ("checkout" , "checkout"), ("cat","category"))
	page = models.CharField(choices = page_choices, max_length = 30)
	category = models.ForeignKey(Category, on_delete = models.CASCADE ,  null = True,  blank = True , related_name='meta')
	title = models.CharField(max_length = 500)
	h1 = models.CharField(max_length = 1000)
	meta_descripton = models.TextField()
	slug = models.SlugField(unique = True,blank = True)

	def __str__(self):
		return self.title

	def clean(self):
		if self.page == "cat" and self.category == None:
			raise ValidationError("Category is a required field now")
		elif(self.page == "home" or self.page == "checkout") and self.category != None:
			raise ValidationError("Category should be empty now")


	def save(self, *arg , **kwargs):
		if self.page == "home" or self.page == "checkout" and self.category == None:
			if self.page == "home":
				print("fgdfg")
				self.slug = "www.rodoinsurance.com"
			else:
				self.slug = "www.rodoinsurance.com/" + slugify(self.page)

		elif self.page == "cat" and self.category == None:
			raise ValidationError("Category is required field now")
		else:
			self.slug = "www.rodoinsurance.com/" + slugify(self.category.name)

		self.h1= self.h1.capitalize()
		super(MetaContent , self).save(*arg ,**kwargs)
		return self.name


class LeaseTerm(models.Model):
	name = models.CharField(max_length = 200)
	content = models.TextField()

	def __str__(self):
		return self.name

class VehicleInformation(models.Model):
	order = models.ForeignKey(Order , on_delete = models.CASCADE)
	leaseterm = models.ForeignKey(LeaseTerm , on_delete = models.DO_NOTHING)
	vehilcle_id = models.CharField(max_length = 200)
	date = models.DateField()
	miles_per_year = models.CharField(max_length = 200)
	monthly_payment = models.FloatField(default=0.0)
	lender = models.CharField(max_length = 200)
	dealer_stock_number = models.CharField(max_length = 200)
	file = models.FileField(upload_to = "Vechile-Documents")

	def __str__(self):
		return self.vehilcle_id

from django.shortcuts import render
from rest_framework import views
from django.db.models import Q
from .models import *
from rest_framework.response import Response
from .serializers import *
from django.http import JsonResponse
from django.conf import settings
import stripe
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.template.defaultfilters import truncatechars_html,truncatechars
from datetime import datetime
# for email
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import smtplib		
from email.mime.text import MIMEText		
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication		
from django.template.loader import render_to_string		
import os, sys

# Create your views here.
class Home(views.APIView):

	def get(self, request ,  *arg, **kwargs):
		"""
		This end point is to get all the categories

		"""

		dictV = {}
		catObj = Category.objects.all().order_by("orderby")
		metaitem = MetaContent.objects.filter(page = "home")
		catobjs = OtherCategorySerializer(catObj, many=True)
		metaserailizer = MetaContentSerailizers(metaitem, many = True)
		response_data = catobjs.data
		dictV['data'] = response_data
		dictV["status"] = True
		dictV["status_code"] = 200
		dictV["message"] = "success"
		dictV["meta"] = metaserailizer.data

		return JsonResponse(dictV)

class CategoryView(views.APIView):

	def get(self, request):

		dictV = {}
		category_id = request.GET.get('slug')

		if not category_id:
			dictV["status"] = False
			dictV["message"] = "Category ID is a required"
			dictV["status_code"] = 200
			dictV['data'] = []
			return JsonResponse(dictV)

		categoryitem = Category.objects.get(slug= category_id)
		serializer = OtherCategorySerializer(categoryitem)
		dictV["status"] = True
		dictV["message"] = "success"
		dictV["status_code"] = 200
		dictV['data'] = serializer.data
		return JsonResponse(dictV)

class Product(views.APIView):
	"""
	This endpoint is to get the product details
	
	"""

	def get(self, request, *arg, **kwargs):

		dictV = {}
		productslug = request.GET.get("productslug")
		if not productslug:
			dictV["status"] = False
			dictV["message"] = "Product slug is a required field"
			dictV["status_code"] = 200
			dictV['data'] = []
			return JsonResponse(dictV)

		productobj = ProductDetail.objects.get(slug = productslug)
		category = productobj.category.id
		metaitems = MetaContent.objects.filter(category__id = category)
		metaserailizer = MetaContentSerailizers(metaitems, many = True)
		# items['meta'] = metaserailizer.data
		trimid = productobj.trim
		otherprod = ProductDetail.objects.filter(trim_id = trimid).exclude(pk = productobj.id)
		serializer = ProductSerializer(productobj)
		otherserilizer = ProductSerializer(otherprod , many = True)
		single_prod_data = serializer.data
		(single_prod_data).update(single_prod_data["category"])
		del single_prod_data["category"]
		single_prod_data["meta"] = metaserailizer.data
		other_pruct_list = []
		for product in otherserilizer.data:
			(product).update(product["category"])
			del product["category"]
			product["short_description"]  = truncatechars_html(product["description"], 20)
			product["image"] = settings.SITE_URL+product["image"]
			other_pruct_list.append(product)
		single_prod_data["image"] = settings.SITE_URL+single_prod_data["image"]
		single_prod_data["short_description"] = truncatechars_html(single_prod_data["description"], 20)
		single_prod_data["short_more_description"] = truncatechars_html(single_prod_data["more_description"], 20)
		dictV["status"] = True
		dictV["message"] = "success"
		dictV["status_code"] = 200
		dictV['data'] = {
				"product" : single_prod_data , 
				"otherproduct"  : other_pruct_list	
					}
		return JsonResponse(dictV)


class  SearchView(views.APIView):
	"""

	TO send the content of the searched data from models
	
	"""

	def get(self, request , *arg , **kwargs):

		""" 

		This endpoint is to submit the search form. you need to send the keyword 'search'. you will get the related models and trim .
		
		"""

		search = request.GET.get('search')
		dictV = {}
		if not search:
			dictV["status"] = False
			dictV["status_code"] = 200
			dictV["message"] = "Search keyword is required"
			dictV['data'] = []
			return JsonResponse(dictV)

		
		try :
			# search in trim model
			items_list = []
			pre_model = ""
			dataObj = {}
			trim_list = []
			trimObj = Trim.objects.filter(Q(trim__icontains = search)|Q(model__model__icontains = search)|Q(model__make__make__icontains = search)
				|Q(model__make__year__year__icontains = search)).order_by("model")
			# trimObj = Trim.objects.all().order_by("model")
			for obj in trimObj:
				trim_dict = {}
				model = obj.model.make.make + " " + obj.model.model
				
				if model != pre_model:
					
					if trim_list:
						dataObj["trim"]=trim_list
						trim_list = []
					if dataObj:
						items_list.append(dataObj)
						dataObj = {}
					dataObj["title"] = model

					pre_model = model
				trim_dict['id']=obj.id
				trim_dict['name']=obj.trim
				trim_dict["make"] = obj.model.make.make
				trim_dict["model"] = obj.model.model
				trim_dict['year']=obj.model.make.year.year
				trim_list.append(trim_dict)
			if trim_list:
				dataObj["trim"]=trim_list
				trim_list = []
			if dataObj:
				items_list.append(dataObj)
				dataObj = {}
			if len(items_list) != 0 :
				dictV["status"] = True
				dictV["status_code"] = 200
				dictV["message"] = "success"
				dictV['data'] = items_list
			else:
				dictV["status"] = True
				dictV["status_code"] = 404
				dictV["message"] = "No item found related to searched keyword."
				dictV['data'] = trim_list
			return JsonResponse(dictV)

		except Exception as e:
			dictV["status"] = False
			dictV["status_code"] = 200
			dictV["message"] = str(e)
			dictV['data'] = []
			return JsonResponse(dictV)

	def post(self, request):

		""" 

		This endpoint is to get the particular search result. you need to send the keyword 'id' which is the id of trim models .
		
		"""

		dictV = {}
		items_list = []
		trimID = request.POST.get("id")
		if not trimID:
			dictV["status_code"] = 404
			dictV["status"] = False
			dictV['data'] = []
			dictV["message"] = "Trim id is required"
			return JsonResponse(dictV)
		productobj = ProductDetail.objects.filter(trim_id = trimID).order_by("category__orderby")
		items = {}
		for item in productobj:
			items = {}
			items['id'] = item.id
			items['name'] = item.category.name
			items['image'] = item.category.image.url
			items['description'] = item.category.description
			items['price'] = item.price
			items['slug'] = item.slug
			items['subtitle'] = item.category.subtitle
			items_list.append(items)

		if productobj:
			dictV["status_code"] = 200
			dictV["status"] = True
			dictV["message"] = "success"
			dictV['data'] = items_list
		else:
			dictV["status_code"] = 404
			dictV["status"] = True
			dictV['data'] = []
			dictV["message"] = "No record associated with given id."
		return JsonResponse(dictV)

class CheckOut(views.APIView):

	"""

	This endpoint is to get all the products on the checkout page. you need to send the 'token'.

	"""


	def post(self, request):
		dictV = {}
		stripe.api_key = settings.STRIPE_SECRET_KEY
		amount = request.data.get("totalamount")
		email = request.data.get("email")
		firstname = request.data.get("firstname")
		lastname = request.data.get("lastname")
		address = str(request.data.get("address1")) + " " + str(request.data.get("address2"))
		state = request.data.get("state")
		city = request.data.get("city")
		zipcode = request.data.get("zipcode")
		orderid = str(request.data.get("orderid"))
		stripeToken = request.data.get('stripeToken')

		#create profile object
		profileObj = Profile.objects.create(email = email)

		# create address object
		addressObj = Address.objects.create(profile = profileObj, first_name = firstname, last_name = lastname, address = address , state = state, city = city, zipcode = zipcode)

		#get order object
		orderobj = Order.objects.get(orderId = orderid)
		orderobj.profile = profileObj

		orderitem = OrderItem.objects.filter(order__orderId = orderid)		
		quantity = len(orderitem)		
		ordets_lists=""		
		itemlist = []		
		for item in orderitem:		
			productdict = {}		
			productdict['name'] = item.product.category.name		
			ordets_lists=ordets_lists+item.product.category.name +  "   " +str(item.product.price)+";"		
			productdict['price'] = item.product.price		
			itemlist.append(productdict)		
		description="Order:     "+str(orderid)+",     Purchased Products:     "+ordets_lists + ",     Customer:     "+firstname + lastname+ "  "+email 		

		try:

			charge = stripe.Charge.create(
			amount=amount,
			currency='usd',
			description=description,
			source= stripeToken,
			metadata={'order_id': orderobj.orderId}
			)

			paid = charge.get('paid')

			if paid == True:
				orderobj.status = True
				orderitem = OrderItem.objects.filter(order__orderId = orderid)
				# quantity = len(orderitem)
				# itemlist = []
				# for item in orderitem:
				# 	productdict = {}
				# 	productdict['name'] = item.product.category.name
				# 	productdict['price'] = item.product.price
				# 	itemlist.append(productdict)

				orderitem.update(transaction_id = charge.get('id'))
				orderobj.save()
				dictV['status_code'] = 200
				dictV['status'] = True
				dictV['message'] = "your payment is successfull"
				dictV['data'] = {}
				dictV['data']['id'] = charge.get('id')
				dictV['data']['shipping'] = charge.get('shipping')
				dictV['data']['currency'] = charge.get('currency')
				dictV['data']['tax'] = charge.get('tax')
				dictV['data']['currency'] = charge.get('currency')
				dictV['data']['affiliation'] = charge.get('affiliation')
				dictV['data']['revenue'] = amount	
				dictV['data']['items'] = itemlist
				dictV['data']['quantity'] = quantity
				return JsonResponse(dictV)

			orderobj.save()
			dictV['status_code'] = 403
			dictV['status'] = False
			dictV['message'] = "Your payment was not successfull"
			dictV['data'] = {}
			return JsonResponse(dictV)

		except Exception as e:
			dictV['status_code'] = 403
			dictV['status'] = False
			dictV['message'] = str(e)
			dictV['data'] = {}
			return JsonResponse(dictV)

@csrf_exempt
def checkoutpage(request):
	if request.method == "POST":
		dictV = {}
		prod =  request.POST.get("products")
		products = [x.strip() for x in prod.split(',')]
		if not products:
			dictV["status_code"] = 404
			dictV["message"] = "Product List is required"
			dictV["status"] = False
			dictV['data'] = []
			return JsonResponse(dictV)
		order_id = request.GET.get("order_id")
		prod_items = [int(id) for id in products]
		product_details = ProductDetail.objects.filter(pk__in=prod_items)
		products = []
		for product in product_details:
			products_list = {}
			products_list["id"] = product.category.id
			products_list["name"] = product.category.name
			products.append(products_list)
		finalprice = sum([product.price for product in product_details])
		if order_id:
			Order.objects.filter(orderId=order_id).delete()

		orderobj = Order.objects.create(totalPrice = finalprice, finalPrice = finalprice, status = False)
		order_items_list = []
		for product in product_details:
			order_items_list.append(OrderItem(order = orderobj,product = product))
		OrderItem.objects.bulk_create(order_items_list)

		publishkey = settings.STRIPE_PUBLISHABLE_KEY
		dictV['status_code'] = 200
		dictV['status'] = True
		dictV['message'] = "success"
		dictV['data'] = {"totalamount" : finalprice ,
						  "products" : products,
						  "order_id" : orderobj.orderId
						  }
		return JsonResponse(dictV)

class LeaseTerms(views.APIView):

	def get(self, request ,  *arg, **kwargs):
		leaseterms = LeaseTerm.objects.all()
		serializer = LeaseTermSerializer(leaseterms, many=True)
		response = {
			"status_code":200,
			"status":True,
			"message":"success",
			"data":serializer.data
		}
		return JsonResponse(response)



class VehicleInfo(views.APIView):

	# def get(self, request ,  *arg, **kwargs):

	# 	context = {}
	# 	orderid = str(request.GET.get('orderid'))
	# 	if orderid == 'None':
	# 		context['status_code'] = 404
	# 		context['status'] = False
	# 		context['message'] = "Order ID required"
	# 		context['data'] = []
	# 		return JsonResponse(context)
	# 	orders = OrderItem.objects.filter(order__orderId = orderid)
	# 	print(orders)
	# 	context['data'] = {}
	# 	order_list = []
	# 	totalamount = 0
	# 	for order in orders:
	# 		orderdict = {}
	# 		orderdict['name'] = order.product.category.__str__()
	# 		orderdict['image'] = settings.SITE_URL + order.product.image.url
	# 		totalamount += order.product.price
	# 		order_list.append(orderdict)
	# 	context['data']['products'] = order_list
	# 	context['data']['totalamount'] = totalamount
	# 	context['status_code'] = 200
	# 	context['status'] = True
	# 	context['message'] = "success"
	# 	return JsonResponse(context)

	def post(self, request ,  *arg, **kwargs):
		response = {}
		order_id = str(request.POST.get("order_id"))
		leaseterm = request.POST.get("leaseterm")
		vehilcle_id = request.POST.get("vehilcle_id")
		date = request.POST.get("date")
		miles_per_year = request.POST.get("miles_per_year")
		monthly_payment = request.POST.get("monthly_payment")
		lender = request.POST.get("lender")
		dealer_stock_number = request.POST.get("dealer_stock_number")
		file =  request.FILES.get("file")
		response['status_code'] = 404
		response['status'] = False
		if not order_id:
			response['message'] = "Order id connot be blank."
		elif not leaseterm:
			response['message'] = "Lease Term connot be blank."
		elif not vehilcle_id:
			response['message'] = "Vehical idetification number id connot be blank."
		elif not date:
			response['message'] = "Date connot be blank."
		elif not miles_per_year:
			response['message'] = "Miles per year connot be blank."
		elif not monthly_payment:
			response['message'] = "Monthly payment connot be blank."
		elif not lender:
			response['message'] = "Lender connot be blank."
		elif not dealer_stock_number:
			response['message'] = "Dealer stock number connot be blank."
		elif not file:
			response['message'] = "Please upload the related documents."
		else:
			try:
				date_obj = datetime.strptime(date, '%Y-%m-%d')
				order = Order.objects.get(orderId=order_id)
				vechileinfo = VehicleInformation.objects.create(
					order = order,
					leaseterm_id=leaseterm,
					vehilcle_id=vehilcle_id,
					date=date_obj.date(),
					miles_per_year=miles_per_year,
					monthly_payment=monthly_payment,
					lender=lender,
					dealer_stock_number=dealer_stock_number,
					file = file
				)
				leaseterm_detail = LeaseTerm.objects.get(id=leaseterm)		
				leaseterm_name = leaseterm_detail.name		
				category_name = []		
				productDetail = ""		
				orderItem = OrderItem.objects.filter(order_id=order.id)		
				for r in range(len(orderItem)):		
					product_id = orderItem[r].product_id		
					productDetail = ProductDetail.objects.get(id=product_id)		
					category_id = productDetail.category_id		
					categoryDetail = Category.objects.get(id=category_id)		
					category_name.append(categoryDetail.name)		
				trimDetail = Trim.objects.get(id=productDetail.trim_id)		
				trim = trimDetail.trim		
				model_id = trimDetail.model_id		
				modelDetail = Model.objects.get(id=model_id)		
				model = modelDetail.model		
				make_id = modelDetail.make_id		
				makeDetail = Make.objects.get(id=make_id)		
				make = makeDetail.make		
				vehicle = make + " " + model + " " + trim		
				profile_id = order.profile_id		
				addressDetail = Address.objects.get(profile_id=profile_id)		
				full_name = addressDetail.first_name + " "  + addressDetail.last_name		
				full_address = addressDetail.address + ", " + addressDetail.city + ", " + addressDetail.state + ", " + addressDetail.zipcode		
				profileDetail = Profile.objects.get(id=profile_id)		
				email = profileDetail.email

				email_from = settings.FROM_EMAIL
				subject = " New order placed on "+datetime.now().strftime("%m/%d/%Y")+ " by "+full_name	
				email_To = [settings.TO_EMAIL,	]		
				html = render_to_string("email_template.html", {'full_name': full_name, 'full_address': full_address, 'email': email, 'category_name': category_name, 'vehicle': vehicle, 'vehilcle_id': vehilcle_id, 'date': date_obj, 'miles_per_year': miles_per_year, 'monthly_payment': monthly_payment, 'leaseterm_name': leaseterm_name, 'lender': lender, 'dealer_stock_number': dealer_stock_number, 'total_price': order.totalPrice, 'order_id': order_id})		
				msg = EmailMessage(subject , html , email_from, email_To )
				msg.content_subtype = "html" 
				file_path = settings.BASE_DIR +  vechileinfo.file.url
				msg.attach_file(file_path)
				msg.send()

				response['status_code'] = 200
				response['status'] = True
				response['message'] = "success"
			except Exception as e:
				raise e
				response['status_code'] = 400
				response['status'] = False
				response['message'] = "Exception raised : " + str(e)

			
		return JsonResponse(response)

class Orders(views.APIView):

	def post(self, request):
		context = {}
		orderid = str(request.POST.get('orderid'))
		if orderid == 'None':
			context['status_code'] = 404
			context['status'] = False
			context['message'] = "Order ID required"
			context['data'] = []
			return JsonResponse(context)
		orders = OrderItem.objects.filter(order__orderId = orderid)
		context['data'] = {}
		order_list = []
		totalamount = 0
		for order in orders:
			orderdict = {}
			orderdict['name'] = order.product.category.__str__()
			orderdict['image'] = settings.SITE_URL + order.product.image.url
			totalamount += order.product.price
			order_list.append(orderdict)

		leaseterm = LeaseTerm.objects.all()
		leasetermserailizer = LeaseTermSerializer(leaseterm , many = True)
		context['data']['products'] = order_list
		context['data']['totalamount'] = totalamount
		context['data']['leaseterm'] = leasetermserailizer.data
		context['status_code'] = 200
		context['status'] = True
		context['message'] = "success"
		return JsonResponse(context)

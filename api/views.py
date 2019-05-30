from django.shortcuts import render
from rest_framework import views
from django.db.models import Q
from .models import *
from rest_framework.response import Response
from .serializers import *
from django.http import JsonResponse
from django.conf import settings
import stripe

# Create your views here.

class Home(views.APIView):

	def get(self, request):
		"""
		This end point is to get all the categories on homepage

		"""

		dictV = {}
		catObj = Category.objects.all()
		catobjs = CategorySerializer(catObj, many=True)
		dictV['data'] = catobjs.data
		dictV["status"] = 200
		dictV["message"] = "success"
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
		try :

			# search in trim model
			items_list = []
			pre_model = ""
			dataObj = {}
			trim_list = []
			trimObj = Trim.objects.filter(Q(trim__icontains = search)|Q(model__model__icontains = search)|Q(model__make__make__icontains = search)).order_by("model")
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
				trim_list.append(trim_dict)
			if trim_list:
				dataObj["trim"]=trim_list
				trim_list = []
			if dataObj:
				items_list.append(dataObj)
				dataObj = {}
			if len(items_list) != 0 :
				dictV["status_code"] = 200
				dictV["status"] = "success"
				dictV['data'] = items_list
			return JsonResponse(dictV)

		except:
			dictV["status"] = 404
			dictV["message"] = "No item found related to searched keyword."
			return JsonResponse(dictV)

	def post(self, request):

		""" 

		This endpoint is to get the particular search result. you need to send the keyword 'id' which is the id of trim models .
		
		"""

		dictV = {}
		items_list = []
		trimID = request.POST.get("id")
		productObj = ProductDetail.objects.filter(trim_id = trimID)
		serializer = ProductSerializer(productObj , many = True)
		if productObj:
			dictV["status_code"] = 200
			dictV["status"] = "true"
			dictV['data'] = serializer.data
		else:
			dictV["status_code"] = 404
			dictV["status"] = "false"
			dictV["message"] = "No record associated with given id."
		return JsonResponse(dictV)

class CheckOut(views.APIView):

	"""

	This endpoin is to get all the products on the checkout page. you need to send the 'token'.

	"""

	def get(self, request):

		dictV = {}
		products = set(request.GET.getlist("products"))
		if not products:
			dictV["status_code"] = 404
			dictV["status"] = "false"
			dictV["message"] = "No product found."
			return JsonResponse(dictV)
		order_id = request.data.get("order_id")
		prod_items = [int(id) for id in products]
		product_details = ProductDetail.objects.filter(pk__in=products)
		products_list = {}
		for product in product_details:
			products_list["id"]=product.category.id
			products_list["name"]=product.category.name
		finalprice = sum([product.price for product in product_details])
		if orderId:
			Order.objects.filter(id=order_id).delete()

		orderobj = Order.objects.create(totalPrice = finalprice, finalPrice = finalprice, status = False)
		order_items_list = []
		for product in product_details:
			order_items_list.append(OrderItem(order = orderobj,product = product))
		OrderItem.objects.bulk_create(order_items_list)
		dictV["message"] = ""

		publishkey = settings.STRIPE_PUBLISHABLE_KEY
		dictV['status_code'] = 200
		dictV["status"] = " true"
		dictV['data'] = {"totalamount" : finalprice ,
						  "products" : products_list,
						  "order_id" : orderobj.orderId
						  }
		return JsonResponse(dictV)

	def post(self, request):

		dictV = {}
		stripe.api_key = settings.STRIPE_SECRET_KEY
		amount = request.data.get("totalamount")
		card_number = request.data.get("card_number")
		cvc = request.data.get("cvc")
		expiry_date = request.data.get("expiry_date")
		email = request.data.get("email")
		firstname = request.data.get("firstname")
		lastname = request.data.get("lastname")
		address = str(request.data.get("address1")) + " " + str(request.data.get("address2"))
		state = request.data.get("state")
		city = request.data.get("city")
		zipcode = request.data.get("zipcode")
		orderid = request.data.get("orderid")
		transaction_id = request.data.get('stripeToken')

		#create profile object
		profileObj = Profile.objects.create(email = email)

		#create cardobject
		# cardObj = CardDetail.objects.create(card_number =  card_number,expiry_date = expiry_date,
		# 	cvc = cvc, profile = profileObj)

		# # create address object
		# addressObj = Address.objects.create(profile = profileObj, first_name = firstname, last_name = lastname, address = address , state = state, city = city, zipcode = zipcode)

		#get order object
		orderobj = Order.objects.get(orderId = orderid)
		orderobj.profile = profileObj

		# charge = stripe.Charge.create(

		# amount=amount,
		# currency='usd',
		# description='RODO',
		# source=request.POST['stripeToken']
		# )
		
		if transaction_id:
			orderobj.status = True
			orderitem = OrderItem.objects.filter(order__orderId = orderid)
			orderitem.update(transaction_id=transaction_id)
			orderobj.save()
			dictV['status'] = 200
			dictV['message'] = "your payment is successfull"
			return JsonResponse(dictV)
		orderobj.save()
		dictV['status'] = 403
		dictV['message'] = "Your payment was not successfull"
		return JsonResponse(dictV)

		
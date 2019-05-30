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

class Category(views.APIView):

	def get(self, request):
		"""
		This end point is to get all the categories

		"""

		dictV = {}
		catObj = Category.objects.all()
		catobjs = CategorySerializer(catObj, many=True)
		dictV['categories'] = catobjs.data
		dictV["status"] = 200
		dictV["message"] = "success"
		return JsonResponse(dictV)

class Product(views.APIView):

	 def get(self, request):
	 	dictV = {}
	 	productid = request.data.get("productid")
	 	productobj = ProductDetail.objects.get(pk = productid)
	 	trimid = productobj.trim
	 	otherprod = ProductDetail.objects.filter(trim_id = trimid).exclude(pk = productid)
	 	serializer = ProductSerializer(productobj)
	 	otherserilizer = ProductSerializer(otherprod , many = True)
	 	dictV["status"] = 200
	 	dictV["message"] = "success"
	 	dictV['data'] = {

					"product" : serializer.data , 
					"otherproduct"  : otherserilizer.data	
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

		search = request.data.get('search')
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
			dictV["status"] = 404
			dictV["message"] = "Object Not Found"
			if len(items_list) != 0 :
				dictV["status"] = 200
				dictV["message"] = "success"
				dictV['data'] = items_list
			return JsonResponse(dictV)

		except:
			dictV["status"] = 404
			dictV["message"] = "Object Not Found"
			return JsonResponse(dictV)

	def post(self, request):

		""" 

		This endpoint is to get the particular search result. you need to send the keyword 'id' which is the id of trim models .
		
		"""

		dictV = {}
		items_list = []
		trimID = request.data.get("id")
		productObj = ProductDetail.objects.filter(trim_id = trimID)
		serializer = ProductSerializer(productObj , many = True)
		if productObj:
			dictV["status"] = 200
			dictV["message"] = "success"
			dictV['data'] = serializer.data
		else:
			dictV["status"] = 404
			dictV["message"] = "Nothing Found"
		return JsonResponse(dictV)

class CheckOut(views.APIView):

	"""

	This endpoin is to get all the products on the checkout page. you need to send the 'token'.

	"""

	def get(self, request):

		dictV = {}
		products = set(request.data.getlist("products"))
		orderId = request.data.get("orderId")
		prod_items = [int(id) for id in products]
		prodObj = ProductDetail.objects.filter(pk__in=products)
		prod_name = [obj.category.name for obj in prodObj]
		finalprice = sum([obj.price for obj in prodObj])
		if orderId:
			orderObj = OrderItem.objects.filter(order__orderId = str(orderId))
			productOrderId = [obj.product.id for obj in orderObj]
			delitem = list(set(productOrderId) - set(prod_items))
			createitem = list(set(prod_items) - set(productOrderId))

			#delete the order item if we have extra id in productOrderId
			if delitem:
				OrderItem.objects.filter(product_id__in = delitem).delete()
				dictV['message'] = "item is deleted "

            # update order if we have extra id in products
			elif createitem:
				orderItemObj = []
				prodObj = ProductDetail.objects.filter(pk__in= createitem)
				for obj in prodObj:
					orderItemObj.append(OrderItem(order = orderObj[0].order,product = obj))
				orderItem = OrderItem.objects.bulk_create(orderItemObj)
				dictV['message'] = "item is created "

			else:
				dictV["message"] = "Nothing to update "

		else:
			orderobj = Order.objects.create(totalPrice = finalprice, finalPrice = finalprice, status = False)
			orderItemObj = []
			for obj in prodObj:
				orderItemObj.append(OrderItem(order = orderobj,product = obj))
			orderObj = OrderItem.objects.bulk_create(orderItemObj)
			dictV["message"] = ""

		publishkey = settings.STRIPE_PUBLISHABLE_KEY
		dictV['status'] = 200
		dictV["message"] += " success"
		dictV['data'] = {"totalamount" : finalprice ,
						  "product_id" : prod_items,
						  "product_name" : prod_name,
						  "order_id" : orderObj[0].order.orderId
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
		cardObj = CardDetail.objects.create(card_number =  card_number,expiry_date = expiry_date,
			cvc = cvc, profile = profileObj)

		# # create address object
		addressObj = Address.objects.create(profile = profileObj, first_name = firstname, last_name = lastname, address = address , state = state, city = city, zipcode = zipcode)

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

		
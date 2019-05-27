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
		for obj in productObj:
			dataObj = {
			"id" : obj.id,
			"price" : obj.price,
			"category" : obj.category.name,
			"category_id" : obj.category.id
			}
			items_list.append(dataObj)
		dictV["status"] = 200
		dictV["message"] = "success"
		dictV['data'] = items_list
		return JsonResponse(dictV)


class AddCart(views.APIView):
	"""

	This view is for adding , viewing and deleting the products in the cart

	"""


	def get(self ,request):
		"""

		This end point is to view all the products in the cart.
		You need to to send the card 'token' each time the user view the cart.
		 
		 """

		dictV = {}
		token = request.data.get('token')
		cartObj = Cart.objects.filter(carttoken__carttoken = token)
		cartvalue = 0
		prod_items = []
		for obj in cartObj:
			prod_dict = {}
			prod_dict['cartID'] =  obj.id
			prod_dict['category'] = obj.product.category.name
			prod_dict['price'] = obj.product.price
			cartvalue += obj.product.price
			prod_items.append(prod_dict)
		dictV['status'] = 200
		dictV["message"] = "success"
		dictV['data'] = {"token" : token,
		                  "cartvalue" : cartvalue ,
						  "product" : prod_items}
		return JsonResponse(dictV)

	def post(self, request):

		""" 

		This endpoint is to add the products in the cart.
		1)For the first time when you add the product in the cart you need to send the 'productId' only.then in response you will get the 'token'
		2)Next time when ever you add the product you just need to send that 'token' along with 'productId' 

		"""
		dictV = {}
		prod_id = request.data.get('productId')
		token = request.data.get('token')
		if token and prod_id:
			tokenObj = CartToken.objects.get(carttoken = token)
			
		else:
			cartObj =  Cart.objects.filter(product_id = prod_id)
			if cartObj:
				dictV["status"] = 400
				dictV["message"] = "Oops! seems like forgot to send the token"
				return JsonResponse(dictV)

			tokenObj = CartToken.objects.create()

		prodObj = ProductDetail.objects.get(id = prod_id)

		#check if object in cart already exist or not
		cartObj = Cart.objects.filter(product = prodObj , carttoken = tokenObj).exists()
		if cartObj:
			dictV["status"] = 400
			dictV["message"] = "Same product in the cart already exist"
			dictV['data'] = {'token' : tokenObj.carttoken}
			return JsonResponse(dictV)

		cartObj = Cart.objects.create(product = prodObj , carttoken = tokenObj)
		dictV["status"] = 200
		dictV["message"] = "success"
		dictV['data'] = {'token' : tokenObj.carttoken}
		return JsonResponse(dictV)

	def delete(self, request):

		"""

		 At this end poin you need to send 'cartID'  to delete the item from the cart 

		 """

		dictV = {}
		cartId =  request.data.get('cartID')
		cartObj = Cart.objects.get(id = cartId)
		token = cartObj.carttoken
		cartObj.delete()
		tokenCount = Cart.objects.filter(carttoken = token).count()
		if tokenCount == 0:
			tokenObj = CartToken.objects.get(carttoken = str(token))
			dictV["status"] = 202
			dictV["message"] = "successfully deleted"
			return JsonResponse(dictV)
		dictV["status"] = 202
		dictV["message"] = "successfully deleted"
		dictV['data'] = {'token' : str(token)}
		return JsonResponse(dictV)

class CheckOut(views.APIView):

	"""

	This endpoin is to get all the products on the checkout page. you need to send the 'token'.

	"""

	def get(self, request):
		dictV = {}
		token = request.data.get('token')
		cartObj = Cart.objects.filter(carttoken__carttoken = token)
		cartvalue = 0
		prod_items = []
		for obj in cartObj:
			prod_dict = {}
			prod_dict['cartID'] =  obj.id
			prod_dict['category'] = obj.product.category.name
			prod_dict['price'] = obj.product.price
			cartvalue += obj.product.price
			prod_items.append(prod_dict)

		publishkey = settings.STRIPE_PUBLISHABLE_KEY
		dictV['status'] = 200
		dictV["message"] = "success"
		dictV['data'] = {"cartvalue" : cartvalue ,
		                  "token" : token,
						  "product" : prod_items,
						  "publishkey" : publishkey
						  }
		return JsonResponse(dictV)

	def post(self, request):

		dictV = {}
		stripe.api_key = settings.STRIPE_SECRET_KEY
		token = request.data.get("token")
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


		#create profile object
		profileObj = Profile.objects.create(email = email)

		#create cardobject
		cardObj = CardDetail.objects.create(card_number =  card_number,expiry_date = expiry_date,
			cvc = cvc, profile = profileObj)

		# create address object
		addressObj = Address.objects.create(profile = profileObj, first_name = firstname, last_name = lastname, address = address , state = state, city = city, zipcode = zipcode)

		#create order object
		orderObj = Order(totalPrice = amount, finalPrice = amount, profile = profileObj )
		charge = stripe.Charge.create(
		amount=amount,
		currency='usd',
		description='RODO',
		source=request.POST['stripeToken']
		)

		transaction_id = request.POST['stripeToken']
		
		if transaction_id:
			orderObj.status = True
		orderObj.save()
		if orderObj.status == True:
			cartObj = Cart.objects.filter(carttoken__carttoken = token)
			prodObj = [obj.product for obj in cartObj]
			orderItemObj = []
			for obj in prodObj:
				orderItemObj.append(OrderItem(order = orderObj,transaction_id =  transaction_id,product = obj))
			orderItem = OrderItem.objects.bulk_create(orderItemObj)

			# empty the cart
			cartObj[0].carttoken.delete()

			dictV['status'] = 200
			dictV['message'] = "your payment is successfull"
			return JsonResponse(dictV)

		dictV['status'] = 400
		dictV['message'] = "Error : Due to some reasons transaction failed"
		return JsonResponse(dictV)
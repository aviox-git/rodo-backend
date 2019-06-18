from rest_framework import serializers
from .models import *

class MakeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Make
		fields = "__all__"

class ModelsSerializer(serializers.ModelSerializer):
	make = MakeSerializer()
	class Meta:
		model = Model
		fields = "__all__"

class TrimSerializer(serializers.ModelSerializer):
	model = ModelsSerializer()
	class Meta:
		model = Trim
		fields = "__all__"


class CategoryNameSerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields =["name",]

class ProductSerializer(serializers.ModelSerializer):
	category = CategoryNameSerializer()
	class Meta:
		model = ProductDetail
		fields = "__all__"

class MetaContentSerailizers(serializers.ModelSerializer):
	
	class Meta:
		model = MetaContent
		fields = ( "h1" , "meta_descripton", "title")

class CategorySerializer(serializers.ModelSerializer):
	meta = MetaContentSerailizers(many=True)

	class Meta:
		model = Category
		fields = ("id" , "name" ,"description" ,"image" , "slug", "meta", "more_description")


class LeaseTermSerializer(serializers.ModelSerializer):
	class Meta:
		model = LeaseTerm
		fields =["id","name",]
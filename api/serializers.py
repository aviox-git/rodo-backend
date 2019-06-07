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

class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
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



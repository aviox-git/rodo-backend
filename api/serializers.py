from rest_framework import serializers
from .models import *
from django.conf import settings

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
	image = serializers.SerializerMethodField()

	class Meta:
		model = Category
		fields = ("id" , "name","subtitle" ,"description" ,"image" , "slug", "meta", "more_description")

	def get_image(self,obj):
		return settings.SITE_URL + obj.image.url

class OtherCategorySerializer(serializers.ModelSerializer):
	meta = MetaContentSerailizers(many=True)
	other_categoreis = serializers.SerializerMethodField()
	image = serializers.SerializerMethodField()

	class Meta:
		model = Category
		fields = ("id" , "name","subtitle","first_section_title","first_section_description" ,"description" ,"image" , "slug", "meta", "more_description", 'other_categoreis')

	def get_image(self,obj):
		return settings.SITE_URL + obj.image.url

	def get_other_categoreis(self, obj):
		category = Category.objects.exclude(pk = obj.pk)
		cat_list = []
		catserailizer = CategorySerializer(category, many = True)
		single_cat = catserailizer.data
		for cat in single_cat:
			cat.pop('more_description')
		return single_cat

class LeaseTermSerializer(serializers.ModelSerializer):
	class Meta:
		model = LeaseTerm
		fields =["id","name",]
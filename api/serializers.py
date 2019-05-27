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
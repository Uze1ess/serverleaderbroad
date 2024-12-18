from rest_framework import serializers
from .models import Student

class YourModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'  # Lấy tất cả các trường, hoặc chỉ định các trường cụ thể

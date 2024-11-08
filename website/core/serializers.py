from rest_framework import serializers

from .models import CommentModel, ResultModel


class LikeToggleSerializer(serializers.Serializer):
    blog_id = serializers.IntegerField()
    

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = ['text']

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultModel
        fields = ['test']
        #fields = '__all__'

    def create(self, validated_data):
        # Using get_or_create to avoid duplicates
        result, created = ResultModel.objects.get_or_create(**validated_data)
        return result
    
    # def create(self, validated_data):
    #     # Check for duplicates before saving
    #     if ResultModel.objects.filter(test=validated_data['test']).exists() and ResultModel.objects.filter(blog=validated_data['blog']).exists():
    #         raise serializers.ValidationError({"field1": "This field1 value already exists."})
        
    #     return super().create(validated_data)
        
from rest_framework import serializers
from .models import FeedbackMessage

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackMessage
        fields = ['id', 'message', 'created_at']
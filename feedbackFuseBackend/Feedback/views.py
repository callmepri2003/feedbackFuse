import json
from django.forms import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import FeedbackMessage
from .serializers import FeedbackSerializer
from rest_framework.exceptions import ParseError
import logging

logger = logging.getLogger(__name__)

class FeedbackListView(generics.ListCreateAPIView):
    """
    Get all feedback messages ordered by newest first
    Submit new feedback message
    """
    queryset = FeedbackMessage.objects.all()
    serializer_class = FeedbackSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            response_data = {
                'count': queryset.count(),
                'results': serializer.data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving feedback: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        try:
            # Validate message
            message = request.data.get('message', None)
            if not message:
                return Response(
                    {'error': 'Message is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            message = message.strip()
            if not message:
                return Response(
                    {'error': 'Message is required and must be between 1-250 characters'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            
            if not message:
                return Response(
                    {'error': 'Message is required and must be between 1-250 characters'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(message) > 250:
                return Response(
                    {'error': 'Message is required and must be between 1-250 characters'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create feedback message
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            feedback = serializer.save()
            
            # Return response matching spec format
            response_data = {
                'id': feedback.id,
                'message': feedback.message,
                'created_at': feedback.created_at.isoformat().replace('+00:00', 'Z')
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ParseError:
            return Response({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except json.JSONDecodeError:
                return Response({'error': 'Invalid JSON in message'}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(
                {'error': 'Message is required and must be between 1-250 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating feedback: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
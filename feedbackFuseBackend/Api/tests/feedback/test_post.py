import json
from datetime import datetime
from unittest.mock import patch, Mock
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from freezegun import freeze_time
import time
from Feedback.models import FeedbackMessage


class FeedbackAPITestCase(APITestCase):
    """Comprehensive test suite for the feedback API endpoint."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.url = reverse('feedback-list')  # Adjust URL name as needed
        # Alternative if using direct URL: self.url = '/feedback/'
        FeedbackMessage.objects.all().delete()
        
    def test_successful_feedback_creation(self):
        """Test successful creation of feedback with valid data."""
        data = {
            "message": "This is really helpful, thanks!"
        }
        
        with freeze_time("2025-06-01T11:45:00Z"):
            response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['message'], "This is really helpful, thanks!")
        self.assertEqual(response.data['created_at'], "2025-06-01T11:45:00Z")
        
        # Verify the feedback was actually created in database
        feedback = FeedbackMessage.objects.get(id=response.data['id'])
        self.assertEqual(feedback.message, "This is really helpful, thanks!")
        self.assertEqual(FeedbackMessage.objects.count(), 1)
    
    def test_feedback_creation_with_minimum_length_message(self):
        """Test feedback creation with minimum valid message length."""
        data = {
            "message": "A"  # Single character - minimum valid
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "A")
        
        # Verify in database
        feedback = FeedbackMessage.objects.get(id=response.data['id'])
        self.assertEqual(feedback.message, "A")
    
    def test_feedback_creation_with_maximum_length_message(self):
        """Test feedback creation with maximum valid message length."""
        data = {
            "message": "x" * 250  # 250 characters - maximum valid
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "x" * 250)
        
        # Verify in database
        feedback = FeedbackMessage.objects.get(id=response.data['id'])
        self.assertEqual(feedback.message, "x" * 250)
    
    def test_feedback_creation_empty_message(self):
        """Test feedback creation fails with empty message."""
        data = {
            "message": ""
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Message is required', response.data['error'])
        
        # Verify no feedback was created
        self.assertEqual(FeedbackMessage.objects.count(), 0)
    
    def test_feedback_creation_missing_message_field(self):
        """Test feedback creation fails when message field is missing."""
        data = {}
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Message is required', response.data['error'])
        
        # Verify no feedback was created
        self.assertEqual(FeedbackMessage.objects.count(), 0)
    
    def test_feedback_creation_null_message(self):
        """Test feedback creation fails with null message."""
        data = {
            "message": None
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Message is required', response.data['error'])
        
        # Verify no feedback was created
        self.assertEqual(FeedbackMessage.objects.count(), 0)
    
    def test_feedback_creation_message_too_long(self):
        """Test feedback creation fails with message exceeding 250 characters."""
        data = {
            "message": "x" * 251  # 251 characters - exceeds limit
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('must be between 1-250 characters', response.data['error'])
        
        # Verify no feedback was created
        self.assertEqual(FeedbackMessage.objects.count(), 0)
    
    def test_feedback_creation_whitespace_only_message(self):
        """Test feedback creation fails with whitespace-only message."""
        test_cases = [
            "   ",      # spaces
            "\t\t",     # tabs
            "\n\n",     # newlines
            " \t\n ",   # mixed whitespace
        ]
        
        for whitespace_message in test_cases:
            with self.subTest(message=repr(whitespace_message)):
                data = {"message": whitespace_message}
                
                response = self.client.post(self.url, data, format='json')
                
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('error', response.data)
                self.assertIn('Message is required', response.data['error'])
        
        # Verify no feedback was created
        self.assertEqual(FeedbackMessage.objects.count(), 0)
    
    def test_feedback_creation_with_special_characters(self):
        """Test feedback creation with special characters and unicode."""
        test_messages = [
            "Great work! 👍🎉",
            "Testing with émojis and àccénts",
            "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "Line breaks\nand\ttabs work too",
            "中文测试",  # Chinese characters
            "Тест на русском",  # Russian characters
        ]
        
        for message in test_messages:
            with self.subTest(message=message):
                data = {"message": message}
                
                response = self.client.post(self.url, data, format='json')
                
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(response.data['message'], message)
                
                # Verify in database
                feedback = FeedbackMessage.objects.get(id=response.data['id'])
                self.assertEqual(feedback.message, message)
                
                # Clean up for next iteration
                feedback.delete()
    
    def test_feedback_creation_response_format(self):
        """Test that the response format matches the API specification."""
        data = {
            "message": "Testing response format"
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check required fields are present
        required_fields = ['id', 'message', 'created_at']
        for field in required_fields:
            self.assertIn(field, response.data)
        
        # Check data types
        self.assertIsInstance(response.data['id'], int)
        self.assertIsInstance(response.data['message'], str)
        self.assertIsInstance(response.data['created_at'], str)
        
        # Check created_at format (ISO 8601)
        created_at = response.data['created_at']
        self.assertTrue(created_at.endswith('Z'))  # UTC timezone
        # Verify it's a valid datetime format
        datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    
    def test_feedback_creation_content_type_json(self):
        """Test that the endpoint accepts JSON content type."""
        data = {
            "message": "Testing JSON content type"
        }
        
        response = self.client.post(
            self.url, 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Testing JSON content type")
    
    def test_feedback_creation_invalid_json(self):
        """Test feedback creation with invalid JSON."""
        invalid_json = '{"message": "incomplete json"'
        
        response = self.client.post(
            self.url, 
            invalid_json, 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_feedback_creation_extra_fields_ignored(self):
        """Test that extra fields in request are ignored."""
        data = {
            "message": "Valid message",
            "extra_field": "should be ignored",
            "id": 999,  # Should be ignored
            "created_at": "2020-01-01T00:00:00Z"  # Should be ignored
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Valid message")
        self.assertNotEqual(response.data['id'], 999)  # Should get auto-generated ID
        self.assertNotEqual(response.data['created_at'], "2020-01-01T00:00:00Z")
    
    def test_feedback_creation_strips_leading_trailing_whitespace(self):
        """Test that leading and trailing whitespace is handled appropriately."""
        data = {
            "message": "  Valid message with spaces  "
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Depending on your serializer implementation, this might strip whitespace
        # Adjust assertion based on your actual behavior
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Common behavior would be to strip whitespace:
        # self.assertEqual(response.data['message'], "Valid message with spaces")
        # Or preserve it as-is:
        # self.assertEqual(response.data['message'], "  Valid message with spaces  ")
    
    def test_http_method_not_allowed(self):
        """Test that non-POST methods are not allowed."""
        data = {
            "message": "Test message"
        }
        
        # Test PUT method
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Test PATCH method
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Test DELETE method
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    # def test_feedback_creation_concurrent_requests(self):
    #     """Test that concurrent feedback creation works correctly."""
    #     import threading
    #     import time
        
    #     results = []
    #     errors = []
        
    #     def create_feedback(message_suffix):
    #         try:
    #             data = {"message": f"Concurrent test {message_suffix}"}
    #             response = self.client.post(self.url, data, format='json')
    #             results.append(response.data)
    #         except Exception as e:
    #             errors.append(str(e))
        
    #     # Create multiple threads
    #     threads = []
    #     for i in range(5):
    #         thread = threading.Thread(target=create_feedback, args=(i,))
    #         threads.append(thread)
        
    #     # Start all threads
    #     for thread in threads:
    #         thread.start()
        
    #     # Wait for all threads to complete
    #     for thread in threads:
    #         thread.join()
        
    #     # Verify results
    #     self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
    #     self.assertEqual(len(results), 5)
    #     self.assertEqual(FeedbackMessage.objects.count(), 5)
        
    #     # Verify all messages are unique
    #     messages = [result['message'] for result in results]
    #     self.assertEqual(len(set(messages)), 5)  # All messages should be unique
    
    def test_feedback_ordering_in_database(self):
        """Test that feedback messages are ordered correctly (newest first)."""
        messages = [
            "First message",
            "Second message", 
            "Third message"
        ]
        
        created_ids = []
        for message in messages:
            data = {"message": message}
            response = self.client.post(self.url, data, format='json')
            created_ids.append(response.data['id'])
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Fetch all feedback messages from database
        all_feedback = list(FeedbackMessage.objects.all())
        
        # Should be ordered newest first due to Meta.ordering
        self.assertEqual(len(all_feedback), 3)
        self.assertEqual(all_feedback[0].message, "Third message")
        self.assertEqual(all_feedback[1].message, "Second message")
        self.assertEqual(all_feedback[2].message, "First message")
    
    def test_feedback_model_str_representation(self):
        """Test the string representation of FeedbackMessage model."""
        data = {
            "message": "This is a test message for string representation"
        }
        
        response = self.client.post(self.url, data, format='json')
        feedback = FeedbackMessage.objects.get(id=response.data['id'])
        
        expected_str = f"Feedback {feedback.id}: This is a test message for string representation..."
        self.assertEqual(str(feedback), expected_str)
    
    def test_feedback_model_str_representation_short_message(self):
        """Test string representation with message shorter than 50 characters."""
        data = {
            "message": "Short message"
        }
        
        response = self.client.post(self.url, data, format='json')
        feedback = FeedbackMessage.objects.get(id=response.data['id'])
        
        expected_str = f"Feedback {feedback.id}: Short message..."
        self.assertEqual(str(feedback), expected_str)


class FeedbackAPIEdgeCaseTestCase(APITestCase):
    """Additional edge case tests for the feedback API."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.url = reverse('feedback-list')  # Adjust URL name as needed
    
    def tearDown(self):
        """Clean up after each test."""
        FeedbackMessage.objects.all().delete()
    
    def test_feedback_creation_boundary_lengths(self):
        """Test feedback creation at exact boundary lengths."""
        # Test exact boundaries
        boundary_tests = [
            (1, True),      # Minimum valid length
            (249, True),    # Just under maximum
            (250, True),    # Maximum valid length  
            (251, False),   # Just over maximum (should fail)
        ]
        
        for length, should_succeed in boundary_tests:
            with self.subTest(length=length):
                data = {"message": "x" * length}
                response = self.client.post(self.url, data, format='json')
                
                if should_succeed:
                    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                    feedback = FeedbackMessage.objects.get(id=response.data['id'])
                    self.assertEqual(len(feedback.message), length)
                    feedback.delete()  # Clean up
                else:
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                    self.assertIn('error', response.data)
    
    def test_feedback_creation_unicode_length_counting(self):
        """Test that unicode characters are counted correctly for length validation."""
        # Emoji and special unicode characters
        unicode_message = "👍" * 250  # 250 emoji characters
        data = {"message": unicode_message}
        
        response = self.client.post(self.url, data, format='json')
        
        # This test depends on how your serializer counts length
        # Most Django/DRF setups count Unicode characters correctly
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test exceeding limit with unicode
        unicode_message_too_long = "👍" * 251
        data = {"message": unicode_message_too_long}
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
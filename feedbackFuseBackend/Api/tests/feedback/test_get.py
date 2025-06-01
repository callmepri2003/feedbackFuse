# Create your tests here.
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from Feedback.models import FeedbackMessage

class FeedbackListTests(APITestCase):
    def setUp(self):
        self.url = reverse('feedback-list')

    def test_get_all_feedback_success(self):
        # Create 2 messages with controlled timestamps
        t1 = make_aware(datetime(2025, 6, 1, 9, 15, 0))
        t2 = make_aware(datetime(2025, 6, 1, 10, 30, 0))

        msg1 = FeedbackMessage.objects.create(message="Could use better mobile responsiveness", created_at=t1)
        msg2 = FeedbackMessage.objects.create(message="Great app! Love the simplicity.", created_at=t2)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure count and structure
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)

        # Ensure order: newest first
        self.assertEqual(response.data['results'][0]['id'], msg2.id)
        self.assertEqual(response.data['results'][1]['id'], msg1.id)

    def test_get_empty_feedback(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])

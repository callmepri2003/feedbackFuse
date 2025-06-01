from django.urls import path
from Feedback import views

urlpatterns = [
    path('feedback/', views.FeedbackListView.as_view(), name='feedback-list'),
]
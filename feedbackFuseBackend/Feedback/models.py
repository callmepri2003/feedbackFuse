from django.db import models

# Create your models here.

class FeedbackMessage(models.Model):
    message = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Newest first
    
    def __str__(self):
        return f"Feedback {self.id}: {self.message[:50]}..."
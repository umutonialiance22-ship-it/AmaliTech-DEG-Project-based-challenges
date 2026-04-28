from django.db import models
from datetime import timedelta
from django.utils import timezone

def is_expired(self):
    return timezone.now() > self.created_at + timedelta(hours=24)

class IdempotencyRecord(models.Model):
    key = models.CharField(max_length=255, unique=True)
    request_body = models.JSONField()
    response_body = models.JSONField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, default="PROCESSING")  # PROCESSING / COMPLETED
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.key
    

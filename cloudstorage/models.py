import uuid
from django.db import models
from django.contrib.auth.models import User

class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    file_size = models.FloatField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # 🔥 NEW FIELD
    share_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True)

    def __str__(self):
        return self.file.name if self.file else "No File"
from django.db import models
from django.conf import settings


class MediaFile(models.Model):
    """Model to store uploaded media files."""
    file = models.FileField(upload_to='media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Media File'
        verbose_name_plural = 'Media Files'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.file.name
    
    def delete(self, *args, **kwargs):
        """Delete the file from storage when the model instance is deleted."""
        storage, path = self.file.storage, self.file.path
        super().delete(*args, **kwargs)
        storage.delete(path)

from django.db import models


class Resume(models.Model):
    filename = models.CharField(max_length=255)
    text = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_file = models.FileField(upload_to='resumes/')

    class Meta:
        app_label = "App"

    def __str__(self):
        return self.filename


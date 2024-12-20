from django.db import models


# Create your models here.
class Message(models.Model):
    username = models.CharField(max_length=250)
    room = models.CharField(max_length=250)
    message = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)

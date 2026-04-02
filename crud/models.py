from django.db import models

# Create your models here.
class Comic(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    img_path = models.CharField(max_length=300)
    price = models.IntegerField()

    def __str__(self):
        return self.title

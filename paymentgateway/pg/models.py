from django.db import models

# Create your models here.
class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)#1,2
    name=models.CharField(max_length=100)
    address=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    contact=models.CharField(max_length=100)
    amount=models.IntegerField(default='0')
from django.db import models
from django.utils import timezone
# Create your models here.
#
class User(models.Model):
    id = models.AutoField("id",primary_key=True)
    username = models.CharField("用户名",max_length=255,default='')
    password = models.CharField("密码",max_length=255,default='')
    creteTime = models.DateField("创建时间",auto_now_add=True)
    email = models.EmailField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'user'
        


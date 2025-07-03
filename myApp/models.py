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


class AirQuality(models.Model):
    city = models.CharField(max_length=100, primary_key=True)  # 👈 单字段主键
    date = models.DateField()
    rank = models.IntegerField()
    prev_rank = models.IntegerField()
    rank_change = models.IntegerField()

    class Meta:
        db_table = 'rank_analysis'
        managed = False  # 表已存在，不让 Django 自动迁移   

     


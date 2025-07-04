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

     
# 年度分析
class YearAirQuality(models.Model):
    city = models.CharField(max_length=50)
    year = models.IntegerField()
    month = models.IntegerField()
    max_PM = models.FloatField()
    min_PM10 = models.FloatField()

    class Meta:
        db_table = 'four'
        managed = False

    def __str__(self):
        return f"{self.city} - {self.year}-{self.month}"


#空气质量地图展示
class dituAirQuality(models.Model):
    city = models.CharField(max_length=100)
    year = models.IntegerField()
    month = models.IntegerField()
    max_AQI = models.FloatField()
    min_AQI = models.FloatField()

    class Meta:
        db_table = 'three'
        managed = False  # 如果是现有表，不生成迁移

    def __str__(self):
        return f"{self.city} {self.year}年{self.month}月 AQI({self.min_AQI}-{self.max_AQI})"


class O3Category(models.Model):
    """O3分类数据表"""
    O3_category = models.CharField(max_length=50, verbose_name="O3分类")
    O3_count = models.IntegerField(verbose_name="数量")
    

    class Meta:
        db_table = 'eught'

    def __str__(self):
        return self.category

class CoCategory(models.Model):
    """CO分类数据表"""
    Co_category = models.CharField(max_length=50, verbose_name="CO分类")
    Co_count = models.IntegerField(verbose_name="数量")
    

    class Meta:
        db_table = 'seven'


    def __str__(self):
        return self.category    


        from django.db import models


# 数据总览
class TableData(models.Model):
    city = models.CharField(max_length=50, verbose_name="城市")
    date = models.DateField(verbose_name="日期")
    airQuality = models.CharField(max_length=50, verbose_name="质量等级")
    AQI = models.IntegerField(verbose_name="AQI")
    rank = models.IntegerField(verbose_name="当日排名")
    PM = models.FloatField(verbose_name="PM2.5")  # 对应原数据的 PM2.5
    PM10 = models.FloatField(verbose_name="PM10")
    So2 = models.FloatField(verbose_name="So2")
    No2 = models.FloatField(verbose_name="No2")
    Co = models.FloatField(verbose_name="Co")
    O3 = models.FloatField(verbose_name="O3")

    class Meta:
        db_table = 'airdata'

    def __str__(self):
        return f"{self.city} - {self.date}"
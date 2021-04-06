from django.db import models

# Create your models here.
class tSeries(models.Model):
    '电视剧基本信息'
    # 属性定义
    sID = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    director = models.CharField(max_length=50)
    starts = models.CharField(max_length=500)
    allNumber = models.IntegerField()

    class Meta:
        db_table = 'tSeries'    # 自定义表名

class tVideo(models.Model):
    '视频基本信息'
    # 属性定义
    uploadID = models.CharField(max_length=100,primary_key=True)
    sID = models.ForeignKey(tSeries,on_delete=models.CASCADE)
    number = models.IntegerField()
    h5Path = models.CharField(max_length=255,unique=True)
    path = models.CharField(max_length=255,unique=True)
    vTime = models.TimeField()
    inputTime = models.DateTimeField()

    class Meta:
        db_table = 'tVideo'    # 自定义表名
from django.db import models

# Create your models here.
class ResVideo(models.Model):
    '视频基本信息'
    # 属性定义
    path = models.CharField(max_length=500,unique=True)
    name = models.CharField(max_length=100)
    totalTime = models.TimeField()
    allNumber = models.IntegerField()
    number = models.IntegerField()
    director = models.CharField(max_length=50)
    starts = models.CharField(max_length=500)
    h5Path = models.CharField(max_length=500,unique=True)

    class Meta:
        db_table = 'resvideo'    # 自定义表名

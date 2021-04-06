from django.db import connection
from detect.models import tSeries


# 根据uploadID获取视频
def getSeriesByID(sID):
    series_obj = tSeries.objects.get(sID=sID)
    return series_obj


def listSeries():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tseries order by name")
    rows = cursor.fetchall()
    series_list = []
    # 遍历查询到的数据
    for row in rows:
        series_obj = tSeries()
        series_obj.sID = row[0]
        series_obj.name = row[1]
        series_obj.director = row[2]
        series_obj.starts = row[3]
        series_obj.allNumber = row[4]
        series_list.append(series_obj)
    return series_list


def deleteSeriesByID(sID):
    series_obj = tSeries.objects.get(sID=sID)
    try:
        series_obj.delete()
    except:
        print("记录已删除！")


# 根据剧名、导演模糊查找
def searchSeriesByWords(searchWords):
    series_list = []
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * from tseries where name like '%"+ searchWords +"%' or director like '%" + searchWords + "%' order by name")
    rows = cursor.fetchall()
    # 遍历查询到的数据
    for row in rows:
        series_obj = tSeries()
        series_obj.sID = row[0]
        series_obj.name = row[1]
        series_obj.director = row[2]
        series_obj.starts = row[3]
        series_obj.allNumber = row[4]
        series_list.append(series_obj)

    return series_list

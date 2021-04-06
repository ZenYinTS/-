import os
import shutil
import time

from django.shortcuts import render, redirect
from detect.models import tSeries

from detect.series.seriesDAO import listSeries, getSeriesByID, deleteSeriesByID, searchSeriesByWords
from detect.video.videoDAO import searchVideoBySID, delVideoByUID
from detect.views import showPageable
from detect.views import access_link, bucket

# 跳转到添加电视剧页面
def seriesAdd(req):
    cont = dict()
    cont["allSeries"] = listSeries()
    cont["op"] = "seriesAdd"
    return render(req, "addSeries.html", cont)

# 添加电视剧
def addSeries(req):
    # 接收参数
    name = req.POST.get("name")
    director = req.POST.get("director")
    starts = req.POST.get("starts")
    allNumber = req.POST.get("allNumber")

    # 新增
    series = tSeries()
    series.name = name
    series.director = director
    series.starts = starts
    series.allNumber = allNumber

    try:
        series.save()
        return redirect("/seriesManage")
    except Exception as e:
        print(e.args)
        return render(req, "addSeries.html")

# 列举所有电视剧
def seriesManageList(req):

    # 获取所有的数据
    series_list = listSeries()
    # 分页显示
    series = showPageable(req,series_list)
    return render(req, 'seriesManage.html', {'series': series})

# 跳转到电视剧编辑页面（和添加电视剧页面共用）
def seriesEdit(req):
    sID = req.GET.get("sID")
    # 遍历查询到的数据
    series_obj = getSeriesByID(sID)
    cont = {"series_obj":series_obj,"op":"seriesEdit"}
    return render(req,"addSeries.html",cont)

# 更新数据库中的视频
def editSeries(req):
    # 接收参数
    sID = req.POST.get("sID")
    name = req.POST.get("name")
    director = req.POST.get("director")
    starts = req.POST.get("starts")
    allNumber = req.POST.get("allNumber")

    series = tSeries.objects.get(sID=sID)
    series.name = name
    series.director = director
    series.starts = starts
    series.allNumber = allNumber

    try:
        series.save()
        return redirect("/seriesManage")
    except Exception as e:
        print(e.args)
        return render(req, "addSeries.html")

# 删除电视剧
def deleteSeries(req):
    sID = req.GET.get("sID")
    # 根据sid找到所有视频删除
    uploadIDs = searchVideoBySID(sID)
    for uploadID in uploadIDs:
        # 数据库记录删除
        path,h5Path= delVideoByUID(uploadID)
        try:
            fileName = "movies/" + path[path.rindex("/") + 1:]
            # 删除云端视频
            bucket.delete_object(fileName)
            # 删除模型文件
            os.remove(h5Path)
        except:
            print("文件不存在或已经删除！")
    # 删除数据库电视剧记录
    deleteSeriesByID(sID)

    return redirect("/seriesManage/list")

# 查找电视剧
def searchSeries(req):
    searchWords = req.GET.get("searchWords")
    # 获取所有的数据
    series_list = searchSeriesByWords(searchWords)
    # 分页显示
    series = showPageable(req, series_list)
    return render(req, 'seriesManage.html', {'series': series,'searchWords':searchWords})
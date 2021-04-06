import os
import shutil
import time
import json
import uuid

from django.shortcuts import render, redirect
from moviepy.editor import VideoFileClip
from django.http import HttpResponse
from oss2 import SizedFileAdapter, determine_part_size
from oss2.models import PartInfo
from detect.FrameOperation import extractFrames, getExtra
from detect.VGGAnalyze import analyze
from detect.models import tVideo

from detect.series.seriesDAO import listSeries
from detect.video.videoDAO import getVideoByUID, listVideos, delVideoByUID, searchVideosByWords
from detect.views import access_link, bucket, showPageable, timeConvert


def manage(req):
    if req.session.get("user") != "admin":
        return redirect("/login")
    return redirect("/videoManage/list")


# 添加视频
def addVideo(req):
    # 接收参数
    uploadID = req.POST.get("uploadID")
    sID = req.POST.get("sID")
    path = req.POST.get("path")
    vTime = req.POST.get("vTime")
    number = req.POST.get("number")

    # 关键帧提取保存在frames/uploadID目录下
    extractFrames(path, uploadID)

    # 训练模型保存static/h5 目录下
    h5Path = analyze(uploadID)

    # 模型训练完成即可删除关键帧
    framesPath = 'detect/frames/' + uploadID
    if os.path.exists(framesPath):
        shutil.rmtree(framesPath)

    # 新增
    video = tVideo()
    video.uploadID = uploadID
    video.sID_id = sID
    video.path = path
    video.vTime = vTime
    video.number = number
    video.h5Path = h5Path
    video.inputTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        if h5Path == "":
            raise Exception("建模失败！")
        video.save()
        return redirect("/videoManage")
    except Exception as e:
        print(e.args)
        return render(req, "addVideo.html")


# 进入添加视频页面
def videoAdd(req):
    cont = dict()
    cont["allSeries"] = listSeries()
    cont["op"] = "videoAdd"
    return render(req, "addVideo.html",cont)


# 上传视频到服务器
def uploadVideo(req):
    uploadID = req.POST.get('uploadID')
    fileName = req.POST.get('fileName')
    file_obj = req.FILES.get('file_obj')
    # 上传文件到对象服务器
    extraName = getExtra(fileName)
    if uploadID == "":
        uploadID = str(uuid.uuid4())
    fileName = "movies/" + uploadID + extraName
    # 断点续传
    breakPointResume(fileName, file_obj)
    # 视频URL
    path = access_link + fileName
    clip = VideoFileClip(path)
    file_time = timeConvert(clip.duration)
    cont = {"uploadID": uploadID, "path": path, "file_time": file_time}
    return HttpResponse(json.dumps(cont), content_type="application/json")


# 断点续传
def breakPointResume(fileName, file):
    total_size = file.size
    # determine_part_size方法用于确定分片大小。
    part_size = determine_part_size(total_size, preferred_size=100 * 1024)

    # 初始化分片。
    upload_id = bucket.init_multipart_upload(fileName).upload_id
    parts = []

    part_number = 1
    offset = 0
    while offset < total_size:
        num_to_upload = min(part_size, total_size - offset)
        # 调用SizedFileAdapter(fileobj, size)方法会生成一个新的文件对象，重新计算起始追加位置。
        result = bucket.upload_part(fileName, upload_id, part_number,
                                    SizedFileAdapter(file, num_to_upload))
        parts.append(PartInfo(part_number, result.etag))

        offset += num_to_upload
        part_number += 1

    # 完成分片上传。
    bucket.complete_multipart_upload(fileName, upload_id, parts)

# 列举所有视频
def videoManageList(req):

    # 获取所有的数据
    video_list = listVideos()
    # 分页显示
    videos = showPageable(req,video_list)
    return render(req, 'videoManage.html', {'videos': videos})

# 跳转到视频编辑页面（和添加视频页面共用）
def videoEdit(req):
    uploadID = req.GET.get("uploadID")
    # 遍历查询到的数据
    video_obj = getVideoByUID(uploadID)
    cont = {"video_obj":video_obj,"allSeries":listSeries(),"op":"videoEdit"}
    return render(req,"addVideo.html",cont)

# 更新数据库中的视频
def editVideo(req):
    # 接收参数
    uploadID = req.POST.get("uploadID")
    sID = req.POST.get("sID")
    path = req.POST.get("path")
    number = req.POST.get("number")

    # 查找到视频对象
    video_obj = getVideoByUID(uploadID)
    h5Path = video_obj.h5Path
    if path != video_obj.path:
        vTime = req.POST.get("vTime")
        # 关键帧提取保存在frames/uploadID目录下
        extractFrames(path, uploadID)
        # 训练模型保存static/h5 目录下
        h5Path = analyze(uploadID)
        # 模型训练完成即可删除关键帧
        framesPath = 'detect/frames/' + uploadID
        if os.path.exists(framesPath):
            shutil.rmtree(framesPath)

    # 更新
    video = tVideo.objects.get(uploadID=uploadID)
    if path != video_obj.path:
        video.path = path
        video.vTime = vTime
        video.h5Path = h5Path

    video.number = number
    video.sID_id = sID

    try:
        if h5Path == "":
            raise Exception("建模失败！")
        video.save()
        return redirect("/videoManage")
    except Exception as e:
        print(e.args)
        return render(req, "addVideo.html")

# 删除视频
def deleteVideo(req):
    uploadID = req.GET.get("uploadID")
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
    return redirect("/videoManage/list")

# 查找视频
def searchVideo(req):
    searchWords = req.GET.get("searchWords")
    # 获取所有的数据
    video_list = searchVideosByWords(searchWords)
    # 分页显示
    videos = showPageable(req, video_list)
    return render(req, 'videoManage.html', {'videos': videos,'searchWords':searchWords})
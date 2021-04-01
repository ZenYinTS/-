import os

from django.http import HttpResponse
from django.shortcuts import render, redirect
from moviepy.editor import VideoFileClip
import oss2
import uuid
from oss2 import SizedFileAdapter, determine_part_size
from oss2.models import PartInfo
import json

# Create your views here.
from detect.FrameOperation import extractFrames
from detect.VGGAnalyze import analyze
from detect.models import ResVideo


# 定义全局变量
# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 分别以HTTP、HTTPS协议访问。
access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', 'LTAI5tKgEGr2SbjzHiG6KKSF')
access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', 'Y2JUwuBaj5FL0n2r797v8xQhWx3Esx')
bucket_name = os.getenv('OSS_TEST_BUCKET', 'zenyints')
endpoint = os.getenv('OSS_TEST_ENDPOINT', 'oss-cn-beijing.aliyuncs.com')
access_link = "https://zenyints.oss-cn-beijing.aliyuncs.com/"
# 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)


def index(req):
    return render(req,"index.html")

def search(req):
    # 确认上面的参数都填写正确了
    for param in (access_key_id, access_key_secret, bucket_name, endpoint):
        assert '<' not in param, '请设置参数：' + param

    picName = req.POST.get("picName", None)
    picture = req.FILES.get("picture", None)
    fileName = upload(picName,picture)    # 上传图片，获取图片在oss中的文件名
    path = access_link + fileName    # 图片访问路径

    # 查询结果
    result = dict()
    # 查找三个最相似的剧集

    return render(req,"index.html",{"picName":picName,"picture":picture,"path":path,"result":result})

# 获取图片扩展命
def getExtra(path):
    index = path.rindex(".")
    return path[index:]

# 本地文件上传
def upload(name,file):
    extraName = getExtra(name)
    fileName = "pic/" + str(uuid.uuid4())+extraName
    bucket.put_object(fileName, file)
    return fileName


# 登录
def login(req):
    account = req.POST.get("account", None)
    password = req.POST.get("password", None)
    if account == "admin" and password == "zengying":
        req.session['user'] = "admin"
        return redirect("/manage")
    return render(req,"login.html")

# 资源管理
def manage(req):
    if req.session.get("user") != "admin":
        return redirect("/login")
    return render(req,"manage.html")

# 添加视频
def addVideo(req):
    # 接收参数
    path = req.POST.get("path")
    name = req.POST.get("name")
    totalTime = req.POST.get("totalTime")
    allNumber = req.POST.get("allNumber")
    number = req.POST.get("number")
    director = req.POST.get("director")
    starts = req.POST.get("starts")

    # 关键帧提取保存在frames目录下
    extractFrames(path)

    # 训练模型保存
    h5Path = analyze(path,access_link,bucket)

    # 新增
    video = ResVideo()
    video.path = path
    video.name = name
    video.totalTime = totalTime
    video.allNumber = allNumber
    video.number = number
    video.director = director
    video.starts = starts
    video.h5Path = h5Path
    cont = dict()
    try:
        if h5Path == "":
            raise Exception("建模失败！")
        video.save()
        cont["msg"] = "添加成功！"
        return render(req,"manage.html",cont)
    except Exception as e:
        print(e.args)
        cont["msg"] = "添加失败！\n" + e.args[0]
        return render(req,"addVideo.html",cont)


# 进入添加视频页面
def add(req):
    return render(req,"addVideo.html")

# 时间格式化
def timeConvert(size):
    M, H = 60, 60 ** 2
    if size < M:
        return '00:00:%02d' % size
    if size < H:
        return '00:%02d:%02d' % (int(size / M), int(size % M))
    else:
        hour = int(size / H)
        mine = int(size % H / M)
        second = int(size % H % M)
        tim_srt = '%02d:%02d:%02d' % (hour, mine, second)
        return tim_srt

# 上传视频到服务器
def uploadVideo(req):
    fileName = req.POST.get('fileName')
    file_obj = req.FILES.get('file_obj')
    # 上传文件到对象服务器
    extraName = getExtra(fileName)
    fileName = "movies/" + str(uuid.uuid4()) + extraName
    uploadVideoMethod(fileName,file_obj)
    # 视频URL
    path = access_link + fileName
    clip = VideoFileClip(path)
    file_time = timeConvert(clip.duration)
    cont = {"path":path,"file_time":file_time}
    # print(file_time)
    return HttpResponse(json.dumps(cont),content_type="application/json")


# 断点续传
def uploadVideoMethod(fileName,file):
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
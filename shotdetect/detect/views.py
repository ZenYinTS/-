import os

from django.shortcuts import render, redirect
import shutil
import oss2
import uuid

# Create your views here.
from detect.models import ResVideo


def index(req):
    return render(req,"index.html")

def upload(req):
    # 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
    # 分别以HTTP、HTTPS协议访问。
    access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', 'LTAI5tKgEGr2SbjzHiG6KKSF')
    access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', 'Y2JUwuBaj5FL0n2r797v8xQhWx3Esx')
    bucket_name = os.getenv('OSS_TEST_BUCKET', 'zenyints')
    endpoint = os.getenv('OSS_TEST_ENDPOINT', 'oss-cn-beijing.aliyuncs.com')

    # 确认上面的参数都填写正确了
    for param in (access_key_id, access_key_secret, bucket_name, endpoint):
        assert '<' not in param, '请设置参数：' + param

    # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
    bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)

    # bucket.put_object('motto.txt', 'Never give up. - Jack Ma')

    path = req.GET.get("path", None)
    extraName = getExtra(path)
    print(path)
    if(os.path.exists(path)):
        localUpload(path,bucket,extraName)
    else:
        netUpload(path,bucket,extraName)
    return render(req,"index.html",{"path":path})

# 获取图片扩展命
def getExtra(path):
    index = path.rindex(".")
    return path[index:]

# 本地图片上传
def localUpload(path,bucket,extraName):
    file = open(path, 'r')
    fileName = uuid.uuid4()
    bucket.put_object(str(fileName)+extraName, file)

# 网络图片上传
def netUpload(path,bucket,extraName):
    pass

# 登录
def login(req):
    # if req.session.get("user") == "admin":
    #     return render(req, "manage.html")
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

    # 上传视频（暂未判断是否是视频文件）
    file = open(path,'r')


    # 新增
    video = ResVideo()
    # video.path = path
    video.name = name
    video.totalTime = totalTime
    video.allNumber = allNumber
    video.number = number
    video.director = director
    video.starts = starts
    cont = dict()
    try:
        video.save()
        cont["msg"] = "添加成功！"
        return render(req,"manage.html",cont)
    except Exception as e:
        print(e)
        cont["msg"] = "添加失败！"
        return render(req,"addVideo.html",cont)


# 进入添加视频页面
def add(req):
    return render(req,"addVideo.html")
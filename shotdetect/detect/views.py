import ast
import json
import os
import re

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.shortcuts import render, redirect
import oss2
import uuid
from django.http import HttpResponse

# Create your views here.
from detect.FrameOperation import getExtra, shotSave
from detect.VGGAnalyze import searchForQuery

# 定义全局变量
# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 分别以HTTP、HTTPS协议访问。
from detect.video.videoDAO import getVideoByUID

access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', 'LTAI5tKgEGr2SbjzHiG6KKSF')
access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', 'Y2JUwuBaj5FL0n2r797v8xQhWx3Esx')
bucket_name = os.getenv('OSS_TEST_BUCKET', 'zenyints')
endpoint = os.getenv('OSS_TEST_ENDPOINT', 'oss-cn-beijing.aliyuncs.com')
access_link = "https://zenyints.oss-cn-beijing.aliyuncs.com/"
# 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)


def index(req):
    return render(req, "index.html")


def search(req):
    # 确认上面的参数都填写正确了
    for param in (access_key_id, access_key_secret, bucket_name, endpoint):
        assert '<' not in param, '请设置参数：' + param

    picName = req.POST.get("picName", None)
    picture = req.FILES.get("picture", None)
    fileName = upload(picName, picture)  # 上传图片

    # 查询结果
    # 查找三个最相似的剧集
    results = searchForQuery("statics" + fileName)  # result{uploadID、frame_time、imgScore}

    for result in results:
        # 根据uploadID找到对象
        video_obj = getVideoByUID(result["uploadID"])
        # 添加对应对象到result中
        result["video_obj"] = video_obj
        # 截图保存
        shotTime = result["frame_time"]
        shotPath = shotSave(video_obj.path,shotTime)
        result["shotPath"] = shotPath

        # 时间格式化
        sTime = timeConvert(shotTime)
        result["sTime"] = sTime

        # 相似度变为百分比形式
        result["imgScore"] = result["imgScore"]*100

    return render(req, "index.html", {"picName": picName, "picture":picture,"path": fileName, "results": results})


# 显示右边详情页面
def showResult(req):
    resVal = req.POST.get('resVal')
    video_pattern = re.compile(r"'video_obj': ({.*?})")
    video_str = re.findall(video_pattern, resVal)[0]
    video_str = re.sub(r", 'vTime': .*?, 'inputTime': .*?\)", "", video_str)
    video_obj = ast.literal_eval(video_str)

    # 获取相似度和所在时间
    result_pattern = re.compile(r", 'video_obj': {.*?}")
    result_str = re.sub(result_pattern, "", resVal)
    result_dict = ast.literal_eval(result_str)

    # 关键信息提取
    cont = dict()
    cont["name"] = video_obj["name"]   # 剧名
    cont["similar"] = str(result_dict["imgScore"]) + " %"  # 相似度
    cont["director"] = video_obj["director"]  # 导演
    cont["starts"] = video_obj["starts"]    # 主演
    cont["allNumber"] = video_obj["allNumber"]    # 总集数
    cont["number"] = video_obj["number"]    # 所在集数
    cont["sTime"] = result_dict["sTime"]    # 所在时间
    cont["src"] = video_obj["path"]    # 视频链接
    cont["frame_time"] = result_dict["frame_time"]    # 跳转时间
    return HttpResponse(json.dumps(cont), content_type="application/json")

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

# 本地图片上传
def upload(name, file):
    extraName = getExtra(name)
    fileName = "/queryPic/" + str(uuid.uuid4()) + extraName
    with open("statics" + fileName, "wb") as image_file:  # 使用二进制的方式打开新建文件，不改变文件，直接写入
        for content in file:
            image_file.write(content)
    return fileName


# 登录
def login(req):
    account = req.POST.get("account", None)
    password = req.POST.get("password", None)
    if account == "admin" and password == "zengying":
        req.session['user'] = "admin"
        return redirect("/manage")
    return render(req, "login.html")

# 分页显示
def showPageable(req,object_list):
    objects = []

    # 将数据按照规定每页显示 10 条, 进行分割
    paginator = Paginator(object_list, 5)

    if req.method == "GET":
        # 获取 url 后面的 page 参数的值, 首页不显示 page 参数, 默认值是 1
        page = req.GET.get('page')
        try:
            objects = paginator.page(page)
        except PageNotAnInteger:
            # 如果请求的页数不是整数, 返回第一页。
            objects = paginator.page(1)
        except EmptyPage:
            # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
            objects = paginator.page(paginator.num_pages)
        except InvalidPage:
            # 如果请求的页数不存在, 重定向页面
            return HttpResponse('找不到页面的内容')
    return objects

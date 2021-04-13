from django.db import connection

# 根据uploadID获取视频
from detect.models import tVideo
from detect.video.VideoVO import VideoVO


def getVideoByUID(uploadID):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT v.*,s.* FROM tvideo as v,tseries as s where v.sID_id  =  s.sID and v.uploadID = '" + uploadID + "'")
    rows = cursor.fetchall()
    # 遍历查询到的数据
    video_obj = VideoVO(rows[0])
    return video_obj


def listVideos():
    cursor = connection.cursor()
    cursor.execute("SELECT v.*,s.* FROM tvideo as v,tseries as s where v.sID_id  =  s.sID order by v.inputTime desc")
    rows = cursor.fetchall()
    video_list = []
    # 遍历查询到的数据
    for row in rows:
        video_list.append(VideoVO(row))
    return video_list


# 删除视频，返回删除视频的视频地址以及模型文件位置
def delVideoByUID(uploadID):
    video_obj = tVideo.objects.get(uploadID=uploadID)
    path = video_obj.path
    h5Path = video_obj.h5Path
    video_obj.delete()
    return (path, h5Path)


# 根据剧名模糊查找、视频位置精确查找视频
def searchVideosByWords(searchWords):
    video_list = []
    cursor = connection.cursor()
    # 查找信息以.mp4结尾，则按照视频链接精确查找
    if str.endswith(searchWords, ".mp4"):
        cursor.execute(
            "SELECT v.*,s.* FROM tvideo as v,tseries as s where v.sID_id  =  s.sID and v.path =" +
            searchWords + "% order by v.inputTime desc")
        rows = cursor.fetchall()
        for row in rows:
            video_list.append(VideoVO(row))
    else:  # 按照剧名模糊查找
        cursor.execute(
            "SELECT v.*,s.* FROM tvideo as v,tseries as s where v.sID_id  =  s.sID and s.name like '%" +
            searchWords + "%' order by v.inputTime desc")
        rows = cursor.fetchall()
        for row in rows:
            video_list.append(VideoVO(row))
    return video_list


# 根据sid找到所有视频，返回id列表
def searchVideoBySID(sID):
    uploadIDs = []
    try:
        videos = tVideo.objects.get(sID=sID)
        for video in videos:
            uploadIDs.append(video.uploadID)
    except:
        print("查询无视频！")
    return uploadIDs

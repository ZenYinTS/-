import os, re
import uuid

ffmpeg = "statics\\ffmpeg-4.3.1\\bin\\ffmpeg.exe"


# 获取图片扩展名
def getExtra(path):
    index = path.rindex(".")
    return path[index:]


# 执行cmd
def execCmd(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text


# 关键帧提取并用关键帧所在时间重命名
def extractFrames(path, uploadID):
    print("-------------- 开始提取关键帧 -------------------")
    # 关键帧提取
    os.mkdir("detect/frames/" + uploadID)
    cmd = ffmpeg + " -i  " + path + " -vf select='eq(pict_type\\,PICT_TYPE_I)' -vsync 2 detect\\frames\\" + uploadID + "\\keyframe-%d.jpg -loglevel debug 2>&1"
    result = execCmd(cmd)
    # 正则匹配，获取I帧的时间点信息
    pat = ".*?pict_type:I.*?"
    typeI = re.findall(pat, result)  # 找到关键帧时间点
    times = []
    for i in typeI:
        pat = "t:(.*?) key:1"
        timeVal = re.findall(pat, i)
        if timeVal == []:
            times.append("")
        else:
            times.append(timeVal[0])
    # 提取出的关键帧以时间点信息重命名
    for i in range(1, len(times) + 1):
        if times[i - 1] == "":
            # 关键帧的时间点丢失，删除该关键帧
            os.remove("detect\\frames\\" + uploadID + "\\keyframe-" + str(i) + ".jpg")
        else:
            # 执行cmd命令实现关键帧重命名
            cmd = "rename detect\\frames\\" + uploadID + "\\keyframe-" + str(i) + ".jpg " + times[i - 1] + ".jpg"
            execCmd(cmd)
    print("已完成重命名！")


# 截图保存，返回截图路径
def shotSave(path, shotTime):
    print("---------------------- result shot ------------------------")
    fileName = "/shot/" + str(uuid.uuid4()) + ".jpg"
    execCmd(ffmpeg + " -i " + path + " -ss " + str(shotTime) + " -vframes 1 statics" + fileName)
    return fileName

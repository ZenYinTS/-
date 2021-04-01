import os, re
import shutil

# 执行cmd
def execCmd(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text

# 关键帧提取并用关键帧所在时间重命名
def extractFrames(path):
    # 判断文件是否存在，存在则删除
    if os.path.exists("detect/frames"):
        shutil.rmtree("detect/frames")
    os.mkdir("detect/frames")
    ffmpeg = "statics\\ffmpeg-4.3.1\\bin\\ffmpeg.exe"
    cmd = ffmpeg + " -i  " + path + " -vf select='eq(pict_type\\,PICT_TYPE_I)' -vsync 2 detect\\frames\\keyframe-%d.jpg -loglevel debug 2>&1"
    # print(cmd)
    result = execCmd(cmd)
    # print(result)
    pat = "t:(.*?) key:1"
    times = re.findall(pat, result)       # 找到关键帧时间点
    for i in range(1,len(times)+1):
        cmd = "rename detect\\frames\\keyframe-"+str(i)+".jpg "+times[i-1]+".jpg"
        execCmd(cmd)
    print("已完成重命名！")

if __name__ == '__main__':
    extractFrames()
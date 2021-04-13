import os
import re
from time import *
import numpy as np
import h5py
import matplotlib.pyplot as  plt

from detect.VGGNet import VGGNet

ffmpeg = "..\\statics\\ffmpeg-4.3.1\\bin\\ffmpeg.exe"

# 执行cmd
def execCmd(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text


def extractFrames(video_link):
    uploadID = video_link.replace("https://zenyints.oss-cn-beijing.aliyuncs.com/movies/","")
    uploadID = uploadID.replace(".mp4","")
    print("-------------- 开始提取关键帧 -------------------")
    # 关键帧提取
    os.mkdir("frames/" + uploadID)
    cmd = ffmpeg + " -i  " + video_link + " -vf select='eq(pict_type\\,PICT_TYPE_I)' -vsync 2 frames\\" + uploadID + "\\keyframe-%d.jpg -loglevel debug 2>&1"
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
            os.remove("frames\\" + uploadID + "\\keyframe-" + str(i) + ".jpg")
        else:
            # 执行cmd命令实现关键帧重命名
            cmd = "rename frames\\" + uploadID + "\\keyframe-" + str(i) + ".jpg " + times[i - 1] + ".jpg"
            execCmd(cmd)
    print("已完成重命名！")
    return uploadID


def get_imlist(path):
    return [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')]

def saveH5(uploadID,num):
    # 提取视频名称作为模型文件名称
    output = "..\\statics\\h5\\" + uploadID + '.h5'
    # print(output)
    img_list = get_imlist('frames\\' + uploadID)
    # print(img_list)
    print("------------------------ feature extraction starts -------------------------------")

    feats = []
    names = []

    model = VGGNet(num)

    for i, img_path in enumerate(img_list):
        norm_feat = model.extractFeat(img_path)  # 修改此处改变提取特征的网络
        img_name = os.path.split(img_path)[1]
        feats.append(norm_feat)
        names.append(img_name)
        print("extracting feature from image No. %d , %d image in total" % ((i + 1), len(img_list)))

    feats = np.array(feats)
    print("--------------------------- writing feature extraction results ----------------------------")
    # 保存h5文件在服务器
    h5f = h5py.File(output, 'w')
    h5f.create_dataset('dataset_1', data=feats)
    h5f.create_dataset('dataset_2', data=np.string_(names))
    h5f.close()
    return output

def getScore(picPath,h5Path,num):
    similarArr = []
    h5f = h5py.File("../statics/h5/" + h5Path, 'r')
    feats = h5f['dataset_1'][:]
    imgNames = h5f['dataset_2'][:]
    h5f.close()

    print("-------------------------- searching starts -----------------------------")
    model = VGGNet(num)
    queryVec = model.extractFeat("frames/"+picPath)  # 计算余弦相似度
    scores = np.dot(queryVec, feats.T)
    rank_ID = np.argsort(scores)[::-1]
    rank_score = scores[rank_ID]

    maxres = 1
    for i, index in enumerate(rank_ID[0:maxres]):
        if rank_score[i] >1:
            rank_score[i] = 1
        similarArr.append((1-rank_score[i])*10e8)
    print(similarArr[0])
    return similarArr[0]

import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = ['KaiTi', 'SimHei', 'FangSong']  # 汉字字体,优先使用楷体，如果找不到楷体，则使用黑体
mpl.rcParams['font.size'] = 12  # 字体大小
mpl.rcParams['axes.unicode_minus'] = False  # 正常显示负号

def showResult(a,b,c,s):
    numArr = []
    scoreArr = []
    timeArr = []
    for num in range(a, b,c):
        if os.path.exists("../statics/h5/"+s+".h5"):
            os.remove("../statics/h5/"+s+".h5")
        # 训练得到h5文件
        saveH5(s, num)
        # 测试输入图像宽度设置对相似度的影响以及h5大小的关系
        start = time()
        score = getScore("test.jpg", s+".h5", num)
        end = time()

        totalTime = end - start
        numArr.append(num)
        scoreArr.append(score)
        timeArr.append(totalTime)
    fig = plt.figure()
    fig.suptitle(t="", fontsize=14, fontweight='bold')
    ax = fig.add_subplot(1, 1, 1)
    ax.set_title("输入层大小与消耗时间的关系")
    ax.set_xlabel("输入层大小(px)")
    ax.set_ylabel("时间(s)")

    ax.plot(numArr, timeArr)

    plt.show()

    # fig = plt.figure()
    # fig.suptitle(t="", fontsize=14, fontweight='bold')
    # ax = fig.add_subplot(1, 1, 1)
    # ax.set_title("输入层大小与相似度的关系")
    # ax.set_xlabel("输入层大小(px)")
    # ax.set_ylabel("相似度")
    plt.figure()
    plt.title("输入层大小与相似度的关系")
    plt.xlabel("输入层大小(px)")
    plt.ylabel("相似度")
    # plt.ylim((0.999990, 1))
    # plt.plot([1,2,3], [0.9999998,1,0.9999981])
    # my_y_ticks = np.arange(0.999990, 1, 0.0000010)
    # ax.yticks(my_y_ticks)
    plt.show()


def resizePic(size,flag):
    originPic = "frames/key.jpg"
    outputPic = "frames/output.jpg"
    if os.path.exists(outputPic):
        os.remove(outputPic)
    # 调用ffmpeg命令
    if flag == "y":
        cmd = ffmpeg + " -i "+originPic+" -vf scale="+str(size)+":-1 "+outputPic
    else:
        cmd = ffmpeg + " -i " + originPic + " -vf scale=" + str(size) + ":"+str(size)+" " + outputPic
    print("正在更改图片为：",size)
    result = execCmd(cmd)
    print(result)
    print("更改成功！")

    

if __name__ == '__main__':
    # video_link = "https://zenyints.oss-cn-beijing.aliyuncs.com/movies/8f178992-db33-4b0f-b87c-6c37ab4a014e.mp4"
    # # 视频抽取关键帧，返回关键帧的保存路径
    # uploadID = extractFrames(video_link)
    # saveH5("8f178992-db33-4b0f-b87c-6c37ab4a014e",194)
    # showResult(32,500,50,"1")
    # print("关键帧原图：")
    # getScore("key.jpg","8f178992-db33-4b0f-b87c-6c37ab4a014e.h5",194)
    # print("关键帧成比例放大：")
    # getScore("big.jpg","8f178992-db33-4b0f-b87c-6c37ab4a014e.h5",194)
    # print("关键帧成比例缩小：")
    # getScore("small.jpg","8f178992-db33-4b0f-b87c-6c37ab4a014e.h5",194)
    # print("与网络输入层宽度相等：")
    # getScore("194.jpg","8f178992-db33-4b0f-b87c-6c37ab4a014e.h5",194)
    # print("比网络输入层宽度大：")
    # getScore("300.jpg","8f178992-db33-4b0f-b87c-6c37ab4a014e.h5",194)
    # print("比网络输入层宽度小：")
    # getScore("100.jpg","8f178992-db33-4b0f-b87c-6c37ab4a014e.h5",194)


    # # 查看分辨率对相似度的影响
    # # 1.成比例
    # simiArr1 = []
    # sizeArr1 = []
    # for size in range(100,300,10):
    #     resizePic(size,"y")
    #     score = getScore("output.jpg","8f178992-db33-4b0f-b87c-6c37ab4a014e.h5",224)
    #     simiArr1.append(score)
    #     sizeArr1.append(size)
    # # 画图
    # fig = plt.figure()
    # fig.suptitle(t="", fontsize=14, fontweight='bold')
    # ax = fig.add_subplot(1, 1, 1)
    # ax.set_title("剧照分辨率对相似度的影响")
    # ax.set_xlabel("剧照分辨率(px)")
    # ax.set_ylabel("相似度")
    #
    # ax.plot(sizeArr1, simiArr1)
    #
    # plt.show()

    # 查看缩放多少时相似度为50%
    # resizePic(70, "y")
    # model = VGGNet(194)
    # test_feats = model.extractFeat("frames\\test.jpg")
    # test1_feats = model.extractFeat("frames\\test1.jpg")
    # scores = np.dot(test_feats,test1_feats.T)
    # print(scores)
    showResult(32,100,10,"1")
    # plt.figure()
    # plt.title("输入层大小与相似度的关系")
    # plt.xlabel("输入层大小(px)")
    # plt.ylabel("相似度")
    # x = [(1-0.9999998)*10e8,0,(1-0.9999981)*10e8]
    # # plt.ylim((0,5000))
    # # plt.yticks(np.arange(0.999990, 1,0.000001))
    # plt.plot([1,2,3],x )
    # # my_y_ticks = np.arange(0.999990, 1, 0.0000010)
    # # ax.yticks(my_y_ticks)
    # plt.show()
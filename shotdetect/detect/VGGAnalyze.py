import h5py
import numpy as np
import os

from detect.FrameOperation import getExtra
from detect.VGGNet import VGGNet


def get_imlist(path):
    return [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')]

def analyze(uploadID):
    # 提取视频名称作为模型文件名称
    output = "statics\\h5\\" + uploadID + '.h5'
    imgList = get_imlist('detect\\frames\\'+uploadID)
    print("--------------------------------  开始提取关键帧特征  --------------------------------")

    feats = []
    names = []

    model = VGGNet()

    for i, imgPath in enumerate(imgList):
        normFeat = model.extractFeat(imgPath)  # 修改此处改变提取特征的网络
        imgName = os.path.split(imgPath)[1]
        feats.append(normFeat)
        names.append(imgName)
        print("正在提取关键帧特征，进度： %d / %d" % ((i + 1), len(imgList)))

    feats = np.array(feats)
    print("--------------------------------  保存关键帧特征中  --------------------------------")
    # 保存h5文件在服务器
    h5f = h5py.File(output, 'w')
    h5f.create_dataset('feats', data=feats)
    h5f.create_dataset('image_name', data=np.string_(names))
    h5f.close()
    return output

def searchForQuery(queryPath):
    similarArr = []
    # 遍历所有h5文件，将每个文件中最相似的一组数据保存在数组中
    for h5Path in os.listdir("statics/h5"):
        # 分析
        uploadID = str.replace(h5Path,".h5","")
        h5f = h5py.File("statics/h5/" + h5Path, 'r')
        feats = h5f['feats'][:]
        imgNames = h5f['image_name'][:]
        h5f.close()

        print("-------------------------- 开始搜索 -----------------------------")
        model = VGGNet()    # 创建模型对象
        queryFeat = model.extractFeat(queryPath)  # 获取图片的特征
        scores = np.dot(queryFeat, feats.T)    # 计算搜索图片与每个关键帧的相似度，得到数组
        rank_ID = np.argsort(scores)[::-1]    # 正序排列scores，返回下标到rank_ID
        rank_score = scores[rank_ID]    # 返回对应rankID的scores值保存在rank_score中

        max_count = 3  # 每部电影都检索出三张相似度最高的图片
        for i, index in enumerate(rank_ID[0:max_count]):
            frame_name = bytes.decode(imgNames[index])
            frame_extra = getExtra(frame_name)
            frame_time = float(str.replace(frame_name,frame_extra,""))
            similarArr.append({"uploadID":uploadID,"frame_time":frame_time ,"imgScore":rank_score[i]})

    # 从所有相似中筛选出三个最相似的
    similarArr.sort(key=lambda x: -x["imgScore"])
    return similarArr[0:3]
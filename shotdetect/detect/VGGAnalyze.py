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
    # print(output)
    img_list = get_imlist('detect\\frames\\'+uploadID)
    # print(img_list)
    print("------------------------ feature extraction starts -------------------------------")

    feats = []
    names = []

    model = VGGNet()

    for i, img_path in enumerate(img_list):
        norm_feat = model.vgg_extract_feat(img_path)  # 修改此处改变提取特征的网络
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

def searchForQuery(queryPath):
    similarArr = []
    # 遍历所有模型，将每个模型中最相似的一组数据保存在数组中
    for h5Path in os.listdir("statics/h5"):
        # 分析
        uploadID = str.replace(h5Path,".h5","")
        h5f = h5py.File("statics/h5/" + h5Path, 'r')
        feats = h5f['dataset_1'][:]
        imgNames = h5f['dataset_2'][:]
        h5f.close()

        print("-------------------------- searching starts -----------------------------")

        # init VGGNet16 model
        model = VGGNet()

        queryVec = model.vgg_extract_feat(queryPath)  # 修改此处改变提取特征的网络
        scores = np.dot(queryVec, feats.T)
        rank_ID = np.argsort(scores)[::-1]
        rank_score = scores[rank_ID]
        # print(rank_score)

        maxres = 3  # 每部电影都检索出三张相似度最高的图片
        for i, index in enumerate(rank_ID[0:maxres]):
            frame_name = bytes.decode(imgNames[index])
            frame_extra = getExtra(frame_name)
            frame_time = float(str.replace(frame_name,frame_extra,""))
            similarArr.append({"uploadID":uploadID,"frame_time":frame_time ,"imgScore":rank_score[i]})

    # 从所有相似中筛选出三个最相似的
    similarArr.sort(key=lambda x: -x["imgScore"])
    # print(similarArr)
    return similarArr[0:3]
import h5py
import numpy as np
import os
from detect.VGGNet import VGGNet


def get_imlist(path):
    return [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')]

# print(get_imlist('frames'))

def analyze(fileName,access_link,bucket):
    # 提取视频名称作为模型文件名称
    fileName = str.replace(fileName,".mp4","")
    fileName = str.replace(fileName,access_link+"movies","")
    output = "h5" + fileName + '.h5'
    # print(output)
    img_list = get_imlist('detect\\frames')
    print(img_list)
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
    # 上传h5文件
    h5f = h5py.File('temp.h5', 'w')
    h5f.create_dataset('dataset_1', data=feats)
    h5f.create_dataset('dataset_2', data=np.string_(names))
    h5f.close()
    h5File = open('temp.h5','rb')
    bucket.put_object(output, h5File)
    h5File.close()
    os.remove('temp.h5')
    return access_link + output

    # 分析
    # query = '1.png'
    # result = 'frames/f1'
    #
    # h5f = h5py.File(index, 'r')
    # feats = h5f['dataset_1'][:]
    # imgNames = h5f['dataset_2'][:]
    # h5f.close()
    #
    # print("---------------------------------------------------------")
    # print("                 searching starts")
    # print("---------------------------------------------------------")
    #
    # # read and show query image
    # queryImg = mpimg.imread(query)
    # plt.title("Query Image")
    # plt.imshow(queryImg)
    # plt.show()
    #
    # # init VGGNet16 model
    # model = VGGNet()
    #
    # queryVec = model.vgg_extract_feat(query)  # 修改此处改变提取特征的网络
    # scores = np.dot(queryVec, feats.T)
    # rank_ID = np.argsort(scores)[::-1]
    # rank_score = scores[rank_ID]
    # # print(rank_score)
    #
    # # number of top retrieved images to show
    # maxres = 3  # 检索出三张相似度最高的图片
    # imlist = []
    # for i, index in enumerate(rank_ID[0:maxres]):
    #     imlist.append(imgNames[index])
    #     print("image names:" + str(imgNames[index]))
    # print("top %d images in order are:" % maxres, imlist)
    # print("score are", rank_score[0:maxres])
    #
    # for i, im in enumerate(imlist):
    #     image = mpimg.imread(result + "/" + str(im, 'utf-8'))
    #     plt.title("search output %d" % (i + 1))
    #     plt.imshow(image)
    #     plt.show()

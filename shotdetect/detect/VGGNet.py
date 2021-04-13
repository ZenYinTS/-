from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing import image
from numpy import linalg
import numpy as np

class VGGNet:
    def __init__(self,num):
        self.num = num
        self.model = VGG16(weights='imagenet',
                               input_shape=(self.num,self.num,3),
                               pooling='max',include_top=False)
        self.model.predict(np.zeros((1,self.num,self.num,3)))

    # 提取图像特征
    def extractFeat(self,path):
        # 对输入图片进行预处理
        img = image.load_img(path,target_size=(self.num,self.num))
        img = image.img_to_array(img)
        img = np.expand_dims(img,axis=0)    # 拓展维度
        img = preprocess_input(img)    # 图像预处理，RGB->BGR，再减去平均值
        # 提取特征
        feat = self.model.predict(img)
        # 特征/范数，使用余弦相似度计算
        normFeat = feat[0] / linalg.norm(feat[0])
        return normFeat
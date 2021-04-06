class VideoVO:
    '视频列表视图对象'
    def __init__(self,tInfo):
        self.uploadID = tInfo[0]
        self.number = tInfo[1]
        self.h5Path = tInfo[2]
        self.path = tInfo[3]
        self.vTime = tInfo[4]
        self.inputTime = tInfo[5]
        self.sID_id = tInfo[6]
        self.sID = tInfo[7]
        self.name = tInfo[8]
        self.director = tInfo[9]
        self.starts = tInfo[10]
        self.allNumber = tInfo[11]

    def __repr__(self):
        return repr(self.__dict__)
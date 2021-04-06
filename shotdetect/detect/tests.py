import ast

from django.test import TestCase

# Create your tests here.
import json
import re
obj_str = "{'uploadID': '66c36ce8-d46e-4fa1-bb4b-329094be9e47', 'frame_time': 27.318958, 'imgScore': 48.84553551673889, 'video_obj': {'uploadID': '66c36ce8-d46e-4fa1-bb4b-329094be9e47', 'number': 6, 'h5Path': 'statics\\h5\\66c36ce8-d46e-4fa1-bb4b-329094be9e47.h5', 'path': 'https://zenyints.oss-cn-beijing.aliyuncs.com/movies/66c36ce8-d46e-4fa1-bb4b-329094be9e47.mp4', 'vTime': datetime.time(0, 24, 15), 'inputTime': datetime.datetime(2021, 4, 6, 3, 11, 41), 'sID_id': 10, 'sID': 10, 'name': '元气少女缘结神', 'director': '未知', 'starts': '未知 ', 'allNumber': 13}, 'shotPath': '/shot/6dc75ad7-ee4e-4600-8c88-6cf8c8cfcf83.jpg', 'sTime': '00:00:27'}"
video_pattern = re.compile(r", 'video_obj': {.*?}")
video_str = re.sub(video_pattern,"",obj_str)
obj_dict = ast.literal_eval(video_str)

# print(video_str)
# video_str = re.sub(r", 'vTime': .*?, 'inputTime': .*?\)", "",video_str)
print(obj_dict)
# print(type (video_str))

# obj_dict = ast.literal_eval(video_str)
# print(obj_dict)
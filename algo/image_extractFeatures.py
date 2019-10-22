import cv2
import numpy as np
import matplotlib.pyplot as plt
from image_preprocess import preprocessImage

class extractImageFeatures:

	def __init__(self, image):
		# - parameter: an image read by cv2.imread()
		self.image = image

	def dHash(self, hash_size=(17, 16)):
		gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
		resized_gray_image = cv2.resize(gray_image, hash_size, interpolation=cv2.INTER_CUBIC)
		dHash_str = ''
		for i in range(hash_size[1]):
			for j in range(hash_size[1]):
				if resized_gray_image[i][j] >= resized_gray_image[i][j + 1]:
					dHash_str = dHash_str + "1"
				else:
					dHash_str = dHash_str + "0"
		return dHash_str

	def hsvHist(self):
		hsv_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
		h, s, v = np.split(hsv_image, 3, axis = 2)
		h = h.reshape((h.shape[0], h.shape[1]))
		s = s.reshape((s.shape[0], s.shape[1]))
		v = v.reshape((v.shape[0], v.shape[1]))
		hsv_matrix = np.ones(h.shape)
		for i in range(h.shape[0]):
			for j in range(h.shape[1]):
				# 对hsv图像先做预处理，接近黑色的均设为黑色，接近白色的均设为白色
				if (v[i][j] < 38):
					h[i][j] = 0
					s[i][j] = 0
					v[i][j] = 0
				elif ((s[i][j] < 26) & (v[i][j] > 204)):
					h[i][j] = 0
					s[i][j] = 0
					v[i][j] = 255
				# 借助上述hsv映射关系，将hsv色彩空间转换为[8, 3, 3]维的空间
				h[i][j] = extractImageFeatures.Hue_list[h[i][j]]
				s[i][j] = extractImageFeatures.Saturation_list[s[i][j]]
				v[i][j] = extractImageFeatures.Value_list[v[i][j]]
				hsv_matrix[i][j] = 9*h[i][j] + 3*s[i][j] + v[i][j]
				hsv_matrix = np.array(hsv_matrix, dtype=np.uint8)
		recoded_hsvHist = cv2.calcHist([hsv_matrix], [0], None, [72], [0, 72]).reshape((1,-1))[0]
		return recoded_hsvHist

	# 下面是一些辅助函数，被声明为类的方法或静态方法
	Hue_list = []
	Saturation_list = []
	Value_list = []
	@classmethod
	def hsv_map(cls):
		cls.Hue_list = np.arange(180)
		cls.Saturation_list = np.arange(256)
		cls.Value_list = np.arange(256)
		for i in range(len(cls.Hue_list)):
			if ((0 <= i) & (i <= 10)) | (158 <= i) & (i <= 180):
				cls.Hue_list[i] = 0
			elif ((11 <= i) & (i <= 20)):
				cls.Hue_list[i] = 1
			elif ((21 <= i) & (i <= 37)):
				cls.Hue_list[i] = 2
			elif ((38 <= i) & (i <= 77)):
				cls.Hue_list[i] = 3
			elif ((78 <= i) & (i <= 95)):
				cls.Hue_list[i] = 4
			elif ((96 <= i) & (i <= 135)):
				cls.Hue_list[i] = 5
			elif ((136 <= i) & (i <= 147)):
				cls.Hue_list[i] = 6
			elif ((148 <= i) & (i <= 157)):
				cls.Hue_list[i] = 7
		for i in range(len(cls.Saturation_list)):
			if ((0 <= i) & (i <= 51)):
				cls.Saturation_list[i] = 0
			elif ((52 <= i) & (i <= 178)):
				cls.Saturation_list[i] = 1
			elif ((179 <= i) & (i <= 256)):
				cls.Saturation_list[i] = 2
		for i in range(len(cls.Value_list)):
			if ((0 <= i) & (i <= 51)):
				cls.Value_list[i] = 0
			elif ((52 <= i) & (i <= 178)):
				cls.Value_list[i] = 1
			elif ((179 <= i) & (i <= 256)):
				cls.Value_list[i] = 2
		return cls.Hue_list,cls.Saturation_list,cls.Value_list

	@staticmethod
	def smoothHist(hist, loop = False):
		new_hist = np.zeros((len(hist)))
		for i in range(len(hist)):
			if i == 0:
				if loop:
					new_hist[i] = (hist[len(hist)-1] + hist[0] + hist[1]) / 3
				else:
					new_hist[i] = (hist[0] + hist[1]) / 2
			if i == len(hist)-1:
				if loop:
					new_hist[i] = (hist[i-1] + hist[i] + hist[0]) / 3
				else:
					new_hist[i] = (hist[i-1] + hist[i]) / 2
			else:
				new_hist[i] = (hist[i-1] + hist[i] + hist[i+1])/3
		return new_hist


if __name__ == "__main__":
	# testing code
	def cmpHash_str(hash_str1, hash_str2):
		n = 0
		if len(hash_str1) != len(hash_str2):
			raise Exception("The input hash strings do not match")
		for i in range(len(hash_str1)):
			if hash_str1[i] != hash_str2[i]:
				n = n + 1
		score = 1 - n / len(hash_str1)
		return score
	def cmpHist(hist1, hist2):
		if not len(hist1) == len(hist2):
			raise Exception("The input hist length should be the same")
		inter = 0.0
		total = 0.01
		for i in range(len(hist1)):
			inter = inter + min(hist1[i], hist2[i])
			total = total + max(hist1[i], hist2[i])
		score = inter / total
		return score
	path1 = "C:\\Users\\Dell\\Desktop\\omi_ori_data\\3a.jpg"
	path2 = "C:\\Users\\Dell\\Desktop\\omi_ori_data\\3b.jpg"

	image1 = cv2.imread(path1)
	obj1_prepro = preprocessImage(image1)
	obj1_prepro.resize_image()
	obj1_prepro.mask_image()
	obj1_extract = extractImageFeatures(obj1_prepro.image)
	extractImageFeatures.hsv_map()
	recoded_hsvHist1 = obj1_extract.hsvHist()

	image2 = cv2.imread(path2)
	obj2_prepro = preprocessImage(image2)
	obj2_prepro.resize_image()
	obj2_prepro.mask_image()
	obj2_extract = extractImageFeatures(obj2_prepro.image)
	extractImageFeatures.hsv_map()
	recoded_hsvHist2 = obj2_extract.hsvHist()
	print(cv2.compareHist(recoded_hsvHist1, recoded_hsvHist2, cv2.HISTCMP_INTERSECT) / np.sum(recoded_hsvHist1))

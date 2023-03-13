import os
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import cv2
import numpy as np
import glob

path = "./train_images/augumented"
folders = os.listdir(path)

#フォルダ名を抽出
classes = [f for f in folders if os.path.isdir(os.path.join(path, f))]
n_classes = len(classes)

# 画像とラベルの格納
X = []
Y = []

for label,class_name in enumerate(classes):
    files = glob.glob(path + "/" + class_name + "/*")
    for file in files:
        img = cv2.imread(file)
        img = cv2.resize(img,dsize=(224,224))
        X.append(img)
        Y.append(label)

# 正規化
X = np.array(X)
X = X.astype('float32')
X /= 255.0

# ラベルの変換
Y = np.array(Y)
Y = to_categorical(Y,n_classes)
Y[:5]

# 学習データとテストデータに分ける(テストデータ2割、学習データ8割)
X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=0.2)
# 学習データ8割
print(X_train.shape)
# テストデータ2割
print(X_test.shape)
# 学習データ8割
print(Y_train.shape)
# テストデータ2割
print(Y_test.shape)

# 参考 https://sasuwo.org/image-classification/#toc2
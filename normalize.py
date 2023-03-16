import os
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import cv2
from keras.applications.vgg16 import VGG16
from keras.models import Sequential
from keras.models import model_from_json
from keras.models import Model
from keras.layers import Input, Activation, Dense, Flatten, Dropout
from tensorflow.keras.optimizers import Adam
import numpy as np
import glob
import pickle

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

# vgg16
input_tensor = Input(shape=(224,224,3))
# 最後の1000の層を省く
base_model = VGG16(weights='imagenet', input_tensor=input_tensor, include_top=False)

# 後付けで入れたい層の作成
top_model = Sequential()
top_model.add(Flatten(input_shape=base_model.output_shape[1:]))
top_model.add(Dense(n_classes, activation='softmax'))

# 結合
model = Model(inputs=base_model.input, outputs=top_model(base_model.output))

# 学習させない層
for layer in model.layers[:15]:
    layer.trainable = False

print('# layers=', len(model.layers))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

model.summary()

# 学習データで学習
model.fit(X_train, Y_train, epochs=20, batch_size=16)

# テストデータで精度確認
score = model.evaluate(X_test, Y_test, batch_size=16)

# クラス名の保存
pickle.dump(classes, open('classes.sav', 'wb'))

# モデルの保存
model.save('cnn.h5')

# 参考 https://sasuwo.org/image-classification/#toc2
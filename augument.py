import os
from tensorflow.keras.preprocessing.image import load_img, img_to_array, ImageDataGenerator
import matplotlib.pyplot as plt
import numpy as np
import shutil
import glob

def generateFiles(files, output_path):
    for i, file in enumerate(files):
        img = load_img(file)
        x = img_to_array(img)
        x = np.expand_dims(x, axis=0)

        # ImageDataGeneratorの生成
        datagen = ImageDataGenerator(
            zca_epsilon=1e-06, # 白色化のイプシロン
            #rotation_range=10.0, # ランダムに回転させる
            width_shift_range=5.0, # ランダムに幅をシフトさせる範囲
            height_shift_range=5.0, # ランダムに高さをシフトさせる範囲
            brightness_range=[0.5, 0.5], # ランダムに明るさを変化させる範囲
            zoom_range=0.0, # ランダムにズームさせる範囲
            horizontal_flip=True, # ランダムに水平方向に反転させる
            vertical_flip=False, # ランダムに垂直方向に反転させる上下が逆になるとひっくり返っているように見えるので垂直方向には反転させない
        )

        dg = datagen.flow(x, batch_size=1, save_to_dir=output_path, save_prefix='img', save_format='jpg')
        for i in range(N_img):
            batch = dg.next()

N_img = 20 # 1枚当たりの水増し枚数

input_path_ok = "./train_images/ok/*"
ok_files = glob.glob(input_path_ok)

output_path_ok = "./train_images/ok_augumented/"
if os.path.isdir(output_path_ok) == True:
    shutil.rmtree(output_path_ok)
os.mkdir(output_path_ok)

input_path_dangerous = "./train_images/dangerous/*"
dangerous_files = glob.glob(input_path_dangerous)

output_path_dangerous = "./train_images/dangerous_augumented/"
if os.path.isdir(output_path_dangerous) == True:
    shutil.rmtree(output_path_dangerous)
os.mkdir(output_path_dangerous)

generateFiles(ok_files, output_path_ok)
generateFiles(dangerous_files, output_path_dangerous)

# 参考: https://algorithm.joho.info/programming/python/flask-keras-image-extend/
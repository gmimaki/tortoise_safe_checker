from tensorflow.keras.preprocessing.image import load_img, img_to_array, ImageDataGenerator
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

N_img = 20 # 1枚当たりの水増し枚数

input_path_ok = "./train_images/ok/*"
ok_files = glob.glob(input_path_ok)

output_path_ok = "./train_images/ok_augumented/"
if os.path.isdir(output_path_ok) == True:
    os.removedirs(output_path_ok)
os.mkdir(output_path_ok)

input_path_dangerous = "./train_images/dangerous/*"
dangerous_file = glob.glob(input_path_dangerous)

output_path_dangerous = "./train_images/dangerous_augumented/"
if os.path.isdir(output_path_dangerous) == True:
    os.removedirs(output_path_dangerous)
os.mkdir(output_path_dangerous)
import matplotlib.pyplot as plt
import glob
import cv2

ok_images = glob.glob("./train_images/ok/*")

image = cv2.imread(ok_images[0])
print(image)
print("HELLO")
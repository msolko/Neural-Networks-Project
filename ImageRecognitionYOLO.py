# -*- coding: utf-8 -*-
from ultralytics import YOLO

import os

#this is here to stop some errors from occurring. It isn't the best practice
#to avoid this error, but results are found when you ignore the problem.
os.environ['KMP_DUPLICATE_LIB_OK']='True' 
#load model
model = YOLO("yolov8n.yaml")

#use model
results = model.train(data="projectconfig.yaml", epochs=1000)


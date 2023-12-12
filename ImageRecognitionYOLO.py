# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 17:49:07 2023

@author: gameb
"""

from ultralytics import YOLO

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
#load model
model = YOLO("yolov8n.yaml")

#use model
results = model.train(data="projectconfig.yaml", epochs=1000)



# model.train(data='mnist160', epochs=10, imgsz=64)

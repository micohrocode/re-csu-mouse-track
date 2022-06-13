# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 10:54:07 2022

@author: mrosa
"""
import cv2 as cv

class Tracker():
    def __init__(self):
        self.highest_y = None
        
    def update(self,detections,image,width):
        # get point closest to the top of the camera
        self.highest_y = min([x[1] for x in detections])
        print(self.highest_y)
        # show line of top point
        cv.line(image, (0,self.highest_y), (width,self.highest_y), (255,0,0), 3)
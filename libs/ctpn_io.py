#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import os
import codecs
from libs.constants import DEFAULT_ENCODING

TXT_EXT = '.txt'
ENCODE_METHOD = DEFAULT_ENCODING

class CtpnWriter:

    def __init__(self, foldername, filename, imgSize, databaseSrc='Unknown', localImgPath=None):
        self.foldername = foldername
        self.filename = filename
        self.databaseSrc = databaseSrc
        self.imgSize = imgSize
        self.boxlist = []
        self.localImgPath = localImgPath
        self.verified = False

    def addBndBox(self, xmin, ymin, xmax, ymax, name, difficult):
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
        bndbox['name'] = name
        bndbox['difficult'] = difficult
        self.boxlist.append(bndbox)

    def BndBox2CtpnLine(self, box, classList=[]):

        xmin = box['xmin']
        xmax = box['xmax']
        ymin = box['ymin']
        ymax = box['ymax']

        # 顺时针方向四点坐标
        x1 = x2 = xmin
        y1 = y4 = ymin
        x3 = x4 = xmax
        y2 = y3 = ymax


        return x1,y1,x2,y2,x3,y3,x4,y4

    def save(self, classList=[], targetFile=None):

        out_file = None #Update yolo .txt

        if targetFile is None:
            out_file = open(
            self.filename + 'ctpn' + TXT_EXT, 'w', encoding=ENCODE_METHOD)
        else:
            out_file = codecs.open(targetFile, 'w', encoding=ENCODE_METHOD)


        for box in self.boxlist:
            x1, y1, x2, y2, x3, y3, x4, y4 = self.BndBox2CtpnLine(box, classList)
            # print (classIndex, xcen, ycen, w, h)
            out_file.write("%d,%d,%d,%d,%d,%d,%d,%d\n" % (x1,y1,x2,y2,x3,y3,x4,y4))



        # print (classList)
        # print (out_class_file)
        # for c in classList:
        #     out_class_file.write(c+'\n')
        #
        # out_class_file.close()
        out_file.close()



class CtpnReader:

    def __init__(self, filepath, image, classListPath=None):
        # shapes type:
        # [labbel, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        self.filepath = filepath

        # if classListPath is None:
        #     dir_path = os.path.dirname(os.path.realpath(self.filepath))
        #     self.classListPath = os.path.join(dir_path, "classes.txt")
        # else:
        #     self.classListPath = classListPath

        # print (filepath, self.classListPath)

        # classesFile = open(self.classListPath, 'r')
        # self.classes = classesFile.read().strip('\n').split('\n')

        # print (self.classes)

        imgSize = [image.height(), image.width(),
                      1 if image.isGrayscale() else 3]

        self.imgSize = imgSize

        self.verified = False
        # try:
        self.parseCtpnFormat()
        # except:
            # pass

    def getShapes(self):
        return self.shapes

    def addShape(self, label, xmin, ymin, xmax, ymax, difficult):

        points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
        self.shapes.append((label, points, None, None, difficult))

    def CtpnLine2Shape(self, x1, y1, x2, y2, x3, y3, x4, y4):
        label = self.classes['text']

        xmin = x1
        xmax = x2
        ymin = y1
        ymax = y3

        # xmin = int(self.imgSize[1] * xmin)
        # xmax = int(self.imgSize[1] * xmax)
        # ymin = int(self.imgSize[0] * ymin)
        # ymax = int(self.imgSize[0] * ymax)

        return label, xmin, ymin, xmax, ymax

    def parseCtpnFormat(self):
        bndBoxFile = open(self.filepath, 'r')
        for bndBox in bndBoxFile:
            x1, y1, x2, y2, x3, y3, x4, y4 = bndBox.split(',')
            label, xmin, ymin, xmax, ymax = self.CtpnLine2Shape(x1, y1, x2, y2, x3, y3, x4, y4)

            # Caveat: difficult flag is discarded when saved as yolo format.
            self.addShape(label, xmin, ymin, xmax, ymax, False)

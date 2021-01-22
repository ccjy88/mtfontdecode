from fontTools.ttLib import TTFont
import numpy as np
import cv2


'''
通过计算font中的Contours面积实现对数字的识别
'''
class FontDecoder(object):
    def __init__(self):
        #不管字体怎么变化，填充面积排序结果是一样的
        self.standarddigit=np.array([7,1,5,3,4,2,9,6,8,0])

    def decodeWoff(self,wofffile,showimg=True):
        font = TTFont(wofffile)
        orders = font.getGlyphOrder()[2:]
        codes = np.array(orders)
        areas=[]
        for code in codes:
            area=self.calcArea(font,code,showimg)
            areas.append(area)
        #print(areas)
        #按面积从小到大排
        areas = np.array(areas)
        indexes = np.argsort(areas)

        realcode = codes[indexes]

        dict={}
        for k,d in zip(realcode,self.standarddigit):
            dict[k[3:].lower()]=d

        #for c in codes:
        #   print('{}={}'.format(c,dict[c]))

        return dict

    #画出图，再缩放
    def calcArea(self,font,code,paintflag=True):
        gly = font['glyf'][code]
        arr = np.array(gly.coordinates.array, np.int)
        arr = np.reshape(arr, (int(len(arr) / 2), 2))
        numcontours = gly.numberOfContours
        endp = gly.endPtsOfContours

        p1 = 0
        contours = []
        area = 0
        for i in range(numcontours):
            p2 = endp[i]
            contourpoint = arr[p1:p2 + 1]
            contours.append(contourpoint)
            p1 = p2 + 1

        img = np.zeros([gly.yMax + 1, gly.xMax + 1], dtype=np.uint8)
        for c in contours:
            c[:,1] = gly.yMax - c[:,1]

            #cv2.drawContours(img, [c], 0 , (255), 10)
            cv2.fillConvexPoly(img,c,(255),1)


        img2 = cv2.resize(img, (400,400))
        if paintflag:
            cv2.imshow('img', img2)
            cv2.waitKey(0)

        #求线的面积
        area = len(img2[img2==255])
        #print(area)
        return area

if __name__ == '__main__':
    fontfile=r'meituan标准1.woff'

    fontdecoder = FontDecoder()
    dict = fontdecoder.decodeWoff(fontfile,showimg=False)
    print(dict)

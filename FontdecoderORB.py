from fontTools.ttLib import TTFont
import numpy as np
import cv2
import re


'''编码对应的字体笔画对应的图像'''
class CodewithImage(object):
    def __init__(self,font,code):
        gly = font['glyf'][code]
        arr = np.array(gly.coordinates.array, np.int)
        arr = np.reshape(arr, (int(len(arr) / 2), 2))
        numcontours = gly.numberOfContours
        endp = gly.endPtsOfContours

        p1 = 0
        contours = []

        for i in range(numcontours):
            p2 = endp[i]
            contourpoint = arr[p1:p2 + 1]
            contours.append(contourpoint)
            p1 = p2 + 1
        #生成图像
        self.imagesorb=[]
        orb = cv2.ORB_create()
        for point1 in contours:
            xmax1 = np.max(point1[:, 0])
            ymax1 = np.max(point1[:, 1])
            img1 = np.zeros([ymax1, xmax1], dtype=np.uint8)
            cv2.drawContours(img1, [point1], -1, (255), 3)

            samesize = 800
            imgsmall1 = cv2.resize(img1, (samesize, samesize))
            # 检测关键点并提取特征
            kp1, des1 = orb.detectAndCompute(imgsmall1, None)
            self.imagesorb.append([kp1, des1])

    def getImageORBs(self):
        return self.imagesorb

class MeituanfontORBDecoder(object):
    def __init__(self):
        #读入标准的woff,就是已知对应数字的woff
        self.stdfn = 'meituan标准1.woff'
        dict = {'e407': 7, 'e0ed': 1, 'f15c': 5, 'ec7f': 3, 'e401': 4, 'e15c': 2, 'e2bd': 9, 'ec9c': 6, 'f0cf': 8, 'e7a2': 0}
        self.stdcodedict={'uni'+k.upper(): v for k,v in dict.items()}
        self.stdfont = TTFont(self.stdfn)
        self.outputcodedigitdict={}

        self.stdcodeimages={}
        orders = self.stdfont.getGlyphOrder()[2:]
        for code in orders:
            codeimg=CodewithImage(self.stdfont,code)
            self.stdcodeimages[code] = codeimg

    def calcImageORB1(self,img1orb,img2orb):
        #orb = cv2.ORB_create()

        # 检测关键点并提取特征
        #kp1, des1 = orb.detectAndCompute(img1, None)
        #kp2, des2 = orb.detectAndCompute(img2, None)

        kp1, des1 = img1orb
        kp2, des2 = img2orb

        # 特征匹配：暴力匹配、汉明距离
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        return len(matches)

        # 绘制特征匹配结果
        #matches = sorted(matches, key=lambda x: x.distance)
        #return matches


    def findUrl(self,text):
        m = re.compile(r'//.*woff')
        pos = m.findall(text)
        if len(pos)>0:
            url = pos[0]
            p = url.rfind('//')
            url = url[p:]
            url = 'https:' + url
            return url
        else:
            return None



    def decodeWoff(self, wofffile, showimg=False):
        font = TTFont(wofffile)
        order = font.getGlyphOrder()[2:]
        result={}
        codeimgs = {}
        for code in order:
            cimg = CodewithImage(font, code)
            codeimgs[code] = cimg
        # 交叉对比
        for code, cimg in codeimgs.items():
            imgs = cimg.getImageORBs()
            stdmatchcodes={}
            for stdcode,stdcimg in self.stdcodeimages.items():
                stdimgs = stdcimg.getImageORBs()
                if len(stdimgs) != len(imgs):
                    continue

                summatch=0
                for i in range(len(imgs)):
                    summatch += self.calcImageORB1(imgs[i],stdimgs[i])
                stdmatchcodes[summatch] = stdcode
            #求最大的
            k = sorted([k for k,v in stdmatchcodes.items()])
            stdcode = stdmatchcodes[k[-1]]
            digit = self.stdcodedict[stdcode]
            result[code[3:].lower()] = digit
        return result

'''    
0e76e872.woff 
{'ef8e': 0, 'edf9': 8, 'e179': 1, 'f8ab': 4, 'e28c': 5, 'e0fc': 7, 'eeea': 3, 'e459': 2, 'ef72': 9, 'e621': 6}
'''
'''
 0e76e872 {'e0fc': 7, 'e179': 1, 'e28c': 5, 'eeea': 3, 'f8ab': 4, 'e459': 2, 'ef72': 9, 'e621': 6, 'edf9': 8, 'ef8e': 0}
'''

if __name__ == '__main__':
        d = MeituanfontORBDecoder()
        dict = d.decodeWoff('0e76e872.woff')
        print(dict)




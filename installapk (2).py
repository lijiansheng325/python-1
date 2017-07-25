# -*- coding:utf-8 -*-
#!/usr/bin/env python 

import os
import sys


doc = "d:\\apk\\04-3rdapk-fromYidao"
apkInstall = "adb install "
txt = "apk.txt"


def findFile():
    apks = os.walk(doc)
    for root,dirs,files in apks:
        for dir in dirs:
#            print(os.path.join(root, dir))
            pass
        for file in files:
            apkFile = os.path.join(root, file)
            f = open(txt, "a")
            f.write(apkFile + '\n')
            f.close()

def installApk(file):
    apkTxt = open(file, "r")
    p = apkTxt.readlines()
    for apk1 in p:
        print "install " + apk1
        os.system(apkInstall + apk1)
def fileExist(file):
    f = os.listdir(".")
    if file in f:
        os.remove(file)
    else:
        pass

if __name__ == "__main__":
    fileExist(txt)

    findFile()
 #   installApk(txt)
    print "finish"

    os.system("pause")

 

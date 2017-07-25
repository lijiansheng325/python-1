#coding=utf-8
#!/usr/bin/env python 

import os
import sys


doc = "d:\\apk\\04-3rdapk-fromYidao"
apkInstall = "adb install "


def findFile():
    apks = os.walk(doc)
    for root,dirs,files in apks:
        for dir in dirs:
#            print(os.path.join(root, dir))
            pass
        for file in files:
            apkFile = os.path.join(root, file)
            f = open("apk.txt", "a")
            f.write(apkFile + '\n')
            f.close()

def installApk(file):
    apkTxt = open(file, "r")
    p = apkTxt.readlines()
    for apk1 in p:
        print "install " + apk1
        os.system(apkInstall + apk1)


if __name__ == "__main__":
    os.remove("apk.txt")
    findFile()
    installApk("apk.txt")
    print "finish"

    os.system("pause")

 

import shutil
import os
from time import sleep

user = os.getlogin()

def export():
    titles = []

    src = f"C:\\Users\\{user}\\AppData\\Local\\osu!\\Songs"
    dst = f"C:\\Users\\{user}\\Music\\osu!player\\Osu"

    files = os.listdir(src)


    for dirname in files:
        i = dirname.index('-')
        title = dirname[i+2:]
        titles.append(title)

    count = 0

    for songdir in files:
        path = src + '\\' + songdir
        for f in os.listdir(path):
            if f.endswith("3") or f.find("audio") == 0:
                tmpsrc = path+'\\'+f
                tmpdst = dst+'\\'+titles[count]+'.mp3'
                shutil.copy(tmpsrc, tmpdst)
                print(str(count)+"/"+str(len(titles)-1) + ':' + titles[count] + '        ' + songdir)
                count += 1

    files = os.listdir(dst)
    test = []

    for song in files:
        if song not in test:
            test.append(song)
        else:
            path = dst + "\\" + song
            os.remove(path)
    files = test
    return files

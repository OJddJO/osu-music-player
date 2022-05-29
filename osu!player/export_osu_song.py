import os
import eyed3
import shutil
from pydub import AudioSegment

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

                if f.endswith("3"):
                    shutil.copy(tmpsrc, tmpdst)
                else:
                    song = AudioSegment.from_file(tmpsrc)
                    song.export(tmpdst, format="mp3")
                
                song = eyed3.load(tmpdst)
                if not song.tag:
                    song.initTag()
                song.tag.album = 'OSU!'
                song.tag.track_num = count + 1

                print(str(count)+"/"+str(len(titles)-1) + ':' + titles[count] + '        ' + songdir)
                count += 1

    files = os.listdir(dst)
    test = []

    for song in files:
        if song not in test:
            if song.endswith("mp3"):
                test.append(song)
            else:
                path = dst + "\\" + song
                os.remove(path)
        else:
            path = dst + "\\" + song
            os.remove(path)
    files = test
    return files

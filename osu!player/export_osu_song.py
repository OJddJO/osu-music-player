import os
import eyed3
import shutil
from pydub import AudioSegment
from thefuzz import fuzz

user = os.getlogin()

def export():
    titles = []
    blacklist = ["<", ">", ":", "\"", "/", "\\", "|", "*", "?"]

    src = f"C:\\Users\\{user}\\AppData\\Local\\osu!\\Songs"
    dst = f"C:\\Users\\{user}\\Music\\osu!player\\Osu"

    files = os.listdir(src)

    try:
        test = eval(open(f'C:\\Users\\{user}\\Music\\osu!player\\import.data').read())
    except:
        test = []

    files2 = []
    for dirname in files:
        if dirname not in test:
            try:
                test.append(dirname)
                path = src + '\\' + dirname
                title = ""
                for f in os.listdir(path):
                    if title == "":
                        if f.endswith(".osu"):
                            tmppath = path + '\\' + f
                            tmp = open(tmppath, encoding="utf-8").read()
                            i = tmp.find("Title:")
                            i2 = tmp.find("TitleUnicode:")
                            if i2 == -1:
                                i2 = tmp.find("Artist:")
                            title = tmp[i+6:i2-1]
                        else:
                            pass
                for blacklisted in blacklist:
                    title = title.replace(blacklisted, "")
                for t in titles:
                    if fuzz.partial_ratio(t, title) >= 90:
                        title = t
                titles.append(title)
                files2.append(dirname)
            except:
                pass


    open(f'C:\\Users\\{user}\\Music\\osu!player\\import.data', 'w').write(str(test))

    if titles == []:
        count = -1
    else:
        count = 0

    if count!=-1:
        for songdir in files2:
            path = src + '\\' + songdir
            fname = ""
            for f in os.listdir(path):
                if fname == "":
                    if f.endswith(".osu"):
                        tmppath = path + '\\' + f
                        tmp = open(tmppath, encoding="utf-8").read()
                        tmp2 = str(fr"{tmp}")
                        i = tmp2.find("AudioFilename:")
                        i2 = tmp2.find("AudioLeadIn:")
                        fname = tmp2[i+15:i2-1]
                    else:
                        pass

            for f in os.listdir(path):
                if f.find(fname) == 0:
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
                    song.tag.album = ''
                    song.tag.date = ''
                    song.tag.artist = ''
                    song.tag.title = titles[count]
                    song.tag.track_num = 0
                    try:
                        song.tag.save()
                    except:
                        "a"

                    print(str(count)+"/"+str(len(titles)-1) + ':' + titles[count] + '        ' + songdir)
                    count += 1   


    files = os.listdir(dst)
    test = []
    return files

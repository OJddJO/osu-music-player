from tkinter import *
from tkinter import filedialog
from pygame import mixer
from pypresence import Presence
from time import time
from random import randint
import os
import os.path
import export_osu_song
import threading
import keyboard
import requests
import webbrowser

user = os.getlogin()
slist = []
run = True

#RPC
start = time()
clientid = '980519752025931836'
try:
    RPC = Presence(clientid)
    RPC.connect()
    print("Discord RPC is ready !")
except:
    print("Discord not found .")


#function
#ask the user for the path of osu! directory
def getPath():
    path = filedialog.askdirectory(title="Select your osu! songs directory")
    if path != "":
        open("path.data", "w").write(path)

#update Discord RPC
state = "Idle"
desc = "    "
def changeStatus():
    global run
    try:
        while run:
            global state, desc
            RPC.update(
                large_image="osu-icon-28",
                large_text="Osu!Player",
                state=state,
                details=desc.replace(".mp3", ""),
                start=start,
                buttons=[{"label": "Download the app", "url": "https://github.com/OJddJO/osu-music-player.exe"}]
            )
    except:
        pass


#Keyboard input
kcontrol = True
def kinput():
    if kcontrol:
        if keyboard.is_pressed('ctrl+alt+space'):
            global state
            if state == 'Paused' or state == 'Idle':
                Play()
                while keyboard.is_pressed('ctrl+alt+space'):
                    'a'
            elif state == 'Listening':
                Pause()
                while keyboard.is_pressed('ctrl+alt+space'):
                    'a'
        elif keyboard.is_pressed('ctrl+alt+left'):
            Previous()
            while keyboard.is_pressed('ctrl+alt+left'):
                'a'
        elif keyboard.is_pressed('ctrl+alt+right'):
            Next()
            while keyboard.is_pressed('ctrl+alt+right'):
                'a'
        elif keyboard.is_pressed('ctrl+alt+up'):
            volume.set(volume.get()+5)
            while keyboard.is_pressed('ctrl+alt+up'):
                'a'
        elif keyboard.is_pressed('ctrl+alt+down'):
            volume.set(volume.get()-5)
            while keyboard.is_pressed('ctrl+alt+down'):
                'a'

#check if a song is playing if not Next()
inactiveTicks = 0
nosong = False
def testPlaying():
    global channel, inactiveTicks, nosong, loop
    if not channel.get_busy():
        if loop:
            if state!='Paused' and state!='Idle':
                inactiveTicks += 1 
                if inactiveTicks == 1000:
                    Next()
        else:
            Stop()
    else:
        inactiveTicks = 0

#import all songs, previously imported songs will not be re-checked -> import.data
def importSongs():
    temp_song=export_osu_song.export()

    for s in temp_song:
        s=s.replace("Osu/","")
        songsList.insert(END,s)
        slist.append(s)

#delete and reimport all songs from osu!
def reimportall():
    global slist, songsList
    root.title("osu!player - Re-importing songs")
    path = 'import.data'
    slist = []
    songsList.delete(0, END)
    os.remove(path)
    path2 = 'Osu\\'
    tmp = os.listdir(path2)
    for element in tmp:
        os.remove(path2+"\\"+element)
    importSongs()
    root.title("osu!player")

#delete current song from listbox
def deletesong():
    curr_song=songsList.curselection()
    songsList.delete(curr_song[0])

#play the selected song or unpause the current song
def Play():
    global desc, state
    if state == "Paused":
        channel.unpause()
        state = "Listening"
    else:
        channel.pause()
        channel.stop()
        song=songsList.get(ACTIVE)
        songsList.selection_set(slist.index(song))
        desc = song
        state = "Listening"
        song=f'Osu\\{song}'
        song = mixer.Sound(song)
        channel.play(song)
    nowplaying.set(f"{state}: {desc}")

#pause the song
def Pause():
    channel.pause()
    global  state
    state = "Paused"
    nowplaying.set(f"{state}: {desc}")

#stop the music channel and reset it
def Stop():
    channel.pause()
    channel.stop()
    songsList.selection_clear(ACTIVE)
    global state, desc
    state = "Idle"
    desc = "    "
    nowplaying.set(f"{state}")

#play previous song
def Previous():
    channel.pause()
    channel.stop()
    global prevx, slist, shuffle
    if shuffle:
        temp2 = slist[prevx[-1]]
        previous_one = songsList.index(prevx[-1])
        if len(prevx)!=1:
            prevx.pop()
    else:
        previous_one=songsList.curselection()
        previous_one=previous_one[0]-1
        if previous_one < 0:
            previous_one = len(slist)-1
        temp2=songsList.get(previous_one)
    global state, desc
    state = "Listening"
    desc = temp2
    temp2=f'Osu\\{temp2}'
    song = mixer.Sound(temp2)
    channel.play(song)
    songsList.selection_clear(0,END)
    songsList.see(previous_one)
    songsList.activate(previous_one)
    songsList.selection_set(previous_one)
    nowplaying.set(f"{state}: {desc}")

#play next song
def Next():
    channel.pause()
    channel.stop()
    global x, shuffle, prevx, slist
    if shuffle:
        prevx.append(slist.index(songsList.get(ACTIVE)))
        x = randint(0, len(slist)-1)
        temp = slist[x]
        next_one = songsList.index(x)
    else:
        next_one=songsList.curselection()
        next_one=next_one[0]+1
        if next_one > len(slist)-1:
            next_one=0
        temp=songsList.get(next_one) 
    global state, desc
    state = "Listening"
    desc = temp
    temp=f'Osu\\{temp}'
    song = mixer.Sound(temp)
    channel.play(song)
    songsList.selection_clear(0,END)
    songsList.see(next_one)
    songsList.activate(next_one)
    songsList.selection_set(next_one)
    nowplaying.set(f"{state}: {desc}")

#toggle loop
loop = True
def Loop():
    global loop, looptxt
    if loop == True:
        loop = False
        looptxt.set("🔁:❎")
    elif loop == False:
        loop = True
        looptxt.set("🔁:✅")

#toggle shuffle
x=0
prevx = []
shuffle = True
def Shuffle():
    global shuffle, shuffletxt
    if shuffle == True:
        shuffle = False
        shuffletxt.set("🔀:❎")
    elif shuffle == False:
        shuffle = True
        shuffletxt.set("🔀:✅")

#toggle keyboard control
def kcstate():
    global kcontrol, kclabel
    if kcontrol == True:
        kcontrol = False
        kclabel.set("⌨:❎")
    elif kcontrol == False:
        kcontrol = True
        kclabel.set("⌨:✅")

#change the volume
regvol = 100
def changeVol():
    global channel, regvol, volume
    regvol = int(volume.get())
    if channel.get_volume() == regvol/100:
        pass
    else:
        channel.set_volume(regvol/100)

#toggle the search bar
def searchToggle():
    if searchBarToggle.get() == 0:
        searchValue.set("")
        searchBar.grid_remove()
        searchTxt.grid_remove()
    elif searchBarToggle.get() == 1:
        searchTxt.grid(row=3, column=0)
        searchBar.grid(row=3, column=1, columnspan=7, pady=5)

#search function to search songs in the app
def search(searchValue):
    songsList.delete(0, END)
    tmp = searchValue.get()
    for element in slist:
        if tmp in element:            
            songsList.insert(END, element)

#window for updates info
def versionWin(update):
    def updateApp():
        webbrowser.open("https://github.com/OJddJO/osu-music-player.exe/releases/latest/")
        vWin.destroy()

    vWin = Toplevel(root)
    vWin.geometry("200x40")
    vWin.iconbitmap("osu-icon-28.ico")
    vWin.config(bg="gray15")
    vWin.title("Check for update")
    vWin.resizable(False, False)

    txt = StringVar()
    txtUpdate = Label(vWin, textvariable=txt)
    txtUpdate.config(bg="gray15", fg="white", bd=0, highlightthickness=0)
    txtUpdate.pack()
    if update:
        txt.set("Update Available !")
        updateButton = Button(vWin, text="Update", command=updateApp)
        updateButton.config(bg="gray40",fg="white",bd=2,highlightthickness=0, relief='groove')
        updateButton.pack()
    else:
        txt.set("Your version is the latest !")
    
    def shutdown():
        vWin.destroy()
    vWin.protocol("WM_DELETE_WINDOW", shutdown)

    threading.Thread(target = vWin.mainloop)

#check version, if not latest open "versionWin" window
update = False
def testVersion(launch=False):
    global update
    version = open("version.lock").read()
    latestVersion = requests.get("https://api.github.com/repos/OJddJO/osu-music-player.exe/releases/latest").json()["tag_name"]
    if version != latestVersion:
        update = True
        if launch:
            versionWin(update)
    if not launch:
        versionWin(update)

#shutdown function
def shutdown():
    global run
    run = False
    root.quit()


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#main config
root=Tk()
root.title('osu!player')
root.resizable(False, False)
root.config(bg="gray15")

mixer.init()
channel = mixer.Channel(1)

#widget
songsList=Listbox(root, selectmode=SINGLE, height=14, width=65)
songsList.config(bg="gray15", fg="white", selectbackground="gray", selectforeground="black", bd=0, highlightthickness=0, font=('arial', 15))
songsList.grid(columnspan=8)

nowplaying=StringVar()
nowplaying.set(f"{state}")
playingLabel=Label(root,textvariable=nowplaying,width=55)
playingLabel.config(bg="gray15", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial', 13))
playingLabel.grid(row=1, column=0, columnspan=6, pady=5)

playButton=Button(root,text="▶", width =4, command=Play)
playButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial',20))
playButton.grid(row=2,column=0, padx=5)

pauseButton=Button(root,text="⏸️", width =4, command=Pause)
pauseButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial',20))
pauseButton.grid(row=2,column=1, padx=5)

stopButton=Button(root,text="⏹️", width =4, command=Stop)
stopButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial',20))
stopButton.grid(row=2,column=2, padx=5)

previousButton=Button(root,text="⏮️", width =4, command=Previous)
previousButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial',20))
previousButton.grid(row=2,column=3, padx=5)

nextButton=Button(root,text="⏭️", width =4, command=Next)
nextButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial',20))
nextButton.grid(row=2,column=4, padx=5)

looptxt = StringVar()
looptxt.set("🔁:✅")
loopButton=Button(root, textvariable=looptxt, width=5, command=Loop)
loopButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial',20))
loopButton.grid(row=2,column=5, padx=5)

shuffletxt = StringVar()
shuffletxt.set("🔀:✅")
shuffleButton=Button(root, textvariable=shuffletxt, width=5, command=Shuffle)
shuffleButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial',20))
shuffleButton.grid(row=2,column=6, padx=5)

kclabel = StringVar()
kclabel.set("⌨:✅")
kc = Button(root, textvariable=kclabel, width=5, command=kcstate)
kc.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial',20))
kc.grid(row=2,column=7)

voltxt = Label(root, bg="gray15", fg="white", text="Volume:")
voltxt.config(font=('arial',12),bd=0,highlightthickness=0)
voltxt.grid(row=1, column=6, pady=5)

volume = Scale(root, from_=0, to=100, orient=HORIZONTAL, variable=IntVar)
volume.config(bg="gray15", fg="white", bd=0, highlightthickness=0)
volume.grid(row=1, column=7, pady=5)
volume.set(100)

searchTxt = Label(root, text="Search:")
searchTxt.config(bg="gray15", fg="white", bd=0, highlightthickness=0, font=('arial',12))
searchValue = StringVar()
searchValue.set("")
searchValue.trace_add("write", lambda name, index, mode, sv=searchValue : search(sv))
searchBar = Entry(root, textvariable=searchValue, width=60)
searchBar.config(bg="gray15", fg="white", bd=2, highlightthickness=0, relief='groove', insertbackground="white", font=('arial', 13))

#menu
menuBar=Menu(root)
root.config(menu=menuBar)

songMenu=Menu(menuBar)
menuBar.add_cascade(label="File",menu=songMenu)
songMenu.add_command(label="Import Songs From Osu!",command=importSongs)
songMenu.add_command(label="Re-import all songs", command=reimportall)
songMenu.add_command(label="Delete song",command=deletesong)
songMenu.add_separator()
songMenu.add_command(label="Select osu! songs directory", command=getPath)

otherMenu = Menu(menuBar)
menuBar.add_cascade(label="Other", menu=otherMenu)
searchBarToggle = IntVar()
searchBarToggle.set(0)
otherMenu.add_command(label="Check for update", command=testVersion)
otherMenu.add_checkbutton(label="Search Bar", variable=searchBarToggle, command=searchToggle)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#run
#test if osu! directory exists
try:
    path = open("path.data").read().replace("/", "\\").replace("user", user)
    if not os.path.exists(path):
        getPath()
except:
    getPath()

importSongs()

#run Discord RPC
threadA = threading.Thread(target= changeStatus)
threadA.start()

#after window creation config (icon and shutdown button)
root.update()
root.iconbitmap("osu-icon-28.ico")
root.protocol("WM_DELETE_WINDOW", shutdown)

#auto check update
testVersion(launch=True)

#mainloop
while run:
    root.update()
    testPlaying()
    changeVol()
    kinput()

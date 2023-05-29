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
        if loop == True:
            if state!='Paused' and state!='Idle':
                inactiveTicks += 1 
                if inactiveTicks == 1000:
                    Next()
        elif loop == "loop":
            if state!='Paused' and state!='Idle':
                inactiveTicks += 1 
                if inactiveTicks == 1000:
                    Play()
        else:
            Stop()
    else:
        inactiveTicks = 0

#import all songs, previously imported songs will not be re-checked -> import.data
def importSongs():
    global slist
    slist = []
    songsList.delete(0, END)
    temp_song=export_osu_song.export()

    for s in temp_song:
        s=s.replace("Osu/","").replace(".mp3","")
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
    path2 = 'Osu'
    tmp = os.listdir(path2)
    for element in tmp:
        os.remove(path2+"\\"+element)
    importSongs()
    root.title("osu!player")

#delete current song from listbox
def deletesong():
    curr_song=songsList.curselection()
    songsList.delete(curr_song[0])

def playSelected(event):
    global desc, state
    channel.pause()
    channel.stop()
    song=songsList.get(ACTIVE)
    songsList.selection_set(slist.index(song))
    desc = song
    state = "Listening"
    song=f'Osu\\{song}.mp3'
    song = mixer.Sound(song)
    channel.play(song)
    nowplaying.set(f"{state}: {desc}")

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
        song=f'Osu\\{song}.mp3'
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
    temp2=f'Osu\\{temp2}.mp3'
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
    temp=f'Osu\\{temp}.mp3'
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
    global loop, loopImage
    loopList = [False, True, "loop"]
    index = loopList.index(loop) + 1
    if index > 2:
        index = 0
    loop = loopList[index]
    if loop == False:
        loop2Button.grid_remove()
        notLoopButton.grid()
    elif loop == True:
        notLoopButton.grid_remove()
        loopButton.grid()
    elif loop == "loop":
        loopButton.grid_remove()
        loop2Button.grid()

#toggle shuffle
x=0
prevx = []
shuffle = True
def Shuffle():
    global shuffle
    if shuffle == True:
        shuffle = False
        shuffleButton.grid_remove()
        notShuffleButton.grid()
    elif shuffle == False:
        shuffle = True
        notShuffleButton.grid_remove()
        shuffleButton.grid()

#toggle keyboard control
def kcstate():
    global kcontrol
    if kcontrol == True:
        kcontrol = False
        kc.grid_remove()
        notKc.grid()
    elif kcontrol == False:
        kcontrol = True
        notKc.grid_remove()
        kc.grid()

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
        searchBar.focus_set()

#search function to search songs in the app
def search(searchValue):
    songsList.delete(0, END)
    tmp = searchValue.get()
    for element in slist:
        if tmp.lower() in element.lower():
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
    #save data to files
    open("data/volume.sav", 'w').write(str(int(volume.get())))
    open("data/shuffle.sav", 'w').write(str(shuffle))
    open("data/loop.sav", 'w').write(str(loop))
    open("data/kcontrol.sav", 'w').write(str(kcontrol))
    run = False
    root.quit()

#playlist functions
def createPlaylist():
    def create():
        name = playlistName.get()
        songs = songsList.curselection()
        songsFile = []
        for index in songs:
            songsFile.append(slist[index])
        if name == "":
            pass
        else:
            open(f"playlists/{name}.txt", 'w').write(str(songsFile))
            playlistWin.destroy()

    def shutdown():
        playlistWin.destroy()

    try:
        os.listdir("playlists")
    except:
        os.mkdir("playlists")

    playlistWin = Toplevel(root)
    playlistWin.iconbitmap("osu-icon-28.ico")
    playlistWin.config(bg="gray15")
    playlistWin.title("Create a playlist")
    playlistWin.resizable(False, False)
    playlistWin.protocol("WM_DELETE_WINDOW", shutdown)

    songsList=Listbox(playlistWin, selectmode=MULTIPLE, height=14, width=50)
    songsList.config(bg="gray15", fg="white", selectbackground="gray", selectforeground="black", bd=0, highlightthickness=0, font=('arial', 15))
    songsList.grid(columnspan=8)

    playlistLabel = Label(playlistWin, text="Name :")
    playlistLabel.config(bg="gray15", fg="white", bd=0, highlightthickness=0)
    playlistLabel.grid(row=1, column=0, pady=5)

    playlistName = StringVar()
    playlistName.set("")
    playlistNameEntry = Entry(playlistWin, textvariable=playlistName, width=40, justify='center')
    playlistNameEntry.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
    playlistNameEntry.grid(row=1, column=1, columnspan=5, pady=5)

    createButton = Button(playlistWin, text="Create", command=create)
    createButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
    createButton.grid(row=1, column=6, pady=5)

    cancelButton = Button(playlistWin, text="Cancel", command=shutdown)
    cancelButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
    cancelButton.grid(row=1, column=7, pady=5)

    temp_song=export_osu_song.export()

    for s in temp_song:
        s=s.replace("Osu/","").replace(".mp3","")
        songsList.insert(END,s)
        slist.append(s)


def importPlaylist():
    def shutdown():
        playlistWin.destroy()

    def usePlaylist():
        global slist
        slist = []
        try:
            i = playlistListbox.curselection()[0]
            playlist = eval(open(f'playlists\\{playlistPath[i]}').read())
            songsList.delete(0, END)
            for element in playlist:
                songsList.insert(END, element)
                slist.append(element)
            playlistWin.destroy()
        except:
            pass

    def changePlaylistName():
        try:
            i = playlistListbox.curselection()[0]
            playlistNameVar.set(playlistPath[i])
        except:
            pass

    playlistWin = Toplevel(root)
    playlistWin.iconbitmap("osu-icon-28.ico")
    playlistWin.config(bg="gray15")
    playlistWin.title("Import a playlist")
    playlistWin.resizable(False, False)
    playlistWin.protocol("WM_DELETE_WINDOW", shutdown)

    playlistListbox = Listbox(playlistWin, selectmode=SINGLE, height=14, width=50)
    playlistListbox.config(bg="gray15", fg="white", selectbackground="gray", selectforeground="black", bd=0, highlightthickness=0, font=('arial', 15))
    playlistListbox.grid(columnspan=8)
    playlistListbox.bind("<Double-Button-1>", lambda args, usePlaylist=usePlaylist: usePlaylist())
    playlistListbox.bind("<Button-1>", lambda args, changePlaylistName=changePlaylistName: changePlaylistName())

    playlistLabel = Label(playlistWin, text="Name:")
    playlistLabel.config(bg="gray15", fg="white", bd=0, highlightthickness=0)
    playlistLabel.grid(row=1, column=0, pady=5)

    playlistNameVar = StringVar()
    playlistNameVar.set("")
    playlistNameLabel = Label(playlistWin, textvariable=playlistNameVar, width=40, justify='center')
    playlistNameLabel.config(bg="gray15", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial', 13))
    playlistNameLabel.grid(row=1, column=1, columnspan=5, pady=5)

    useButton = Button(playlistWin, text="Select", command=usePlaylist)
    useButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
    useButton.grid(row=1, column=6, pady=5)

    cancelButton = Button(playlistWin, text="Cancel", command=shutdown)
    cancelButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
    cancelButton.grid(row=1, column=7, pady=5)

    playlistPath = []
    for element in os.listdir("playlists"):
        if element.endswith(".txt"):
            playlistPath.append(element)
            playlistName = element.replace(".txt", "")
            playlistListbox.insert(END, playlistName)


def deletePlaylist():
    def shutdown():
        playlistWin.destroy()

    def delete():
        try:
            i = playlistListbox.curselection()[0]
            os.remove(f"playlists\\{playlistPath[i]}")
            playlistWin.destroy()
        except:
            pass

    def changePlaylistName():
        try:
            i = playlistListbox.curselection()[0]
            playlistNameVar.set(playlistPath[i])
        except:
            pass

    playlistWin = Toplevel(root)
    playlistWin.iconbitmap("osu-icon-28.ico")
    playlistWin.config(bg="gray15")
    playlistWin.title("Delete a playlist")
    playlistWin.resizable(False, False)
    playlistWin.protocol("WM_DELETE_WINDOW", shutdown)

    playlistListbox = Listbox(playlistWin, selectmode=SINGLE, height=14, width=50)
    playlistListbox.config(bg="gray15", fg="white", selectbackground="gray", selectforeground="black", bd=0, highlightthickness=0, font=('arial', 15))
    playlistListbox.grid(columnspan=8)
    playlistListbox.bind("<Double-Button-1>", lambda args, usePlaylist=delete: usePlaylist())
    playlistListbox.bind("<Button-1>", lambda args, changePlaylistName=changePlaylistName: changePlaylistName())

    playlistLabel = Label(playlistWin, text="Name:")
    playlistLabel.config(bg="gray15", fg="white", bd=0, highlightthickness=0)
    playlistLabel.grid(row=1, column=0, pady=5)

    playlistNameVar = StringVar()
    playlistNameVar.set("")
    playlistNameLabel = Label(playlistWin, textvariable=playlistNameVar, width=40, justify='center')
    playlistNameLabel.config(bg="gray15", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial', 13))
    playlistNameLabel.grid(row=1, column=1, columnspan=5, pady=5)

    deleteButton = Button(playlistWin, text="Delete", command=delete)
    deleteButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
    deleteButton.grid(row=1, column=6, pady=5)

    cancelButton = Button(playlistWin, text="Cancel", command=shutdown)
    cancelButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
    cancelButton.grid(row=1, column=7, pady=5)

    playlistPath = []
    for element in os.listdir("playlists"):
        if element.endswith(".txt"):
            playlistPath.append(element)
            playlistName = element.replace(".txt", "")
            playlistListbox.insert(END, playlistName)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#main config
root=Tk()
root.title('osu!player')
root.resizable(False, False)
root.config(bg="gray15")

mixer.init()
channel = mixer.Channel(1)

#widget
songsList=Listbox(root, selectmode=SINGLE, height=14, width=70)
songsList.config(bg="gray15", fg="white", selectbackground="gray", selectforeground="black", bd=0, highlightthickness=0, font=('arial', 15))
songsList.grid(columnspan=8)
songsList.bind("<Double-Button-1>", playSelected)

nowplaying=StringVar()
nowplaying.set(f"{state}")
playingLabel=Label(root,textvariable=nowplaying,width=60)
playingLabel.config(bg="gray15", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial', 13))
playingLabel.grid(row=1, column=0, columnspan=6, pady=5)

playImage = PhotoImage(file="icon/play_button.png")
playButton=Button(root, image=playImage, command=Play)
playButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
playButton.grid(row=2,column=0, padx=5)

pauseImage = PhotoImage(file="icon/pause_button.png")
pauseButton=Button(root, image=pauseImage, command=Pause)
pauseButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
pauseButton.grid(row=2,column=1, padx=5)

stopImage = PhotoImage(file="icon/stop_button.png")
stopButton=Button(root, image=stopImage, command=Stop)
stopButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
stopButton.grid(row=2,column=2, padx=5)

previousImage = PhotoImage(file="icon/previous_button.png")
previousButton=Button(root, image=previousImage, command=Previous)
previousButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
previousButton.grid(row=2,column=3, padx=5)

nextImage = PhotoImage(file="icon/next_button.png")
nextButton=Button(root, image=nextImage, command=Next)
nextButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
nextButton.grid(row=2,column=4, padx=5)

loopImage = PhotoImage(file="icon/loop_button.png")
loopButton=Button(root, image=loopImage, command=Loop)
loopButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
loopButton.grid(row=2,column=5, padx=5)
loopButton.grid_remove()
notLoopImage = PhotoImage(file="icon/not_loop_button.png")
notLoopButton=Button(root, image=notLoopImage, command=Loop)
notLoopButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
notLoopButton.grid(row=2,column=5, padx=5)
notLoopButton.grid_remove()
loop2Image = PhotoImage(file="icon/loop2_button.png")
loop2Button=Button(root, image=loop2Image, command=Loop)
loop2Button.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
loop2Button.grid(row=2,column=5, padx=5)
loop2Button.grid_remove()

shuffleImage = PhotoImage(file="icon/shuffle_button.png")
shuffleButton=Button(root, image=shuffleImage, command=Shuffle)
shuffleButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
shuffleButton.grid(row=2,column=6, padx=5)
notShuffleImage = PhotoImage(file="icon/not_shuffle_button.png")
notShuffleButton = Button(root, image=notShuffleImage, command=Shuffle)
notShuffleButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
notShuffleButton.grid(row=2,column=6, padx=5)
notShuffleButton.grid_remove()

kcImage = PhotoImage(file="icon/keyboard_button.png")
kc = Button(root, image=kcImage, command=kcstate)
kc.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
kc.grid(row=2,column=7, padx=5)
notKcImage = PhotoImage(file="icon/not_keyboard_button.png")
notKc = Button(root, image=notKcImage, command=kcstate)
notKc.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
notKc.grid(row=2,column=7, padx=5)
notKc.grid_remove()

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
menuBar.add_cascade(label="Songs",menu=songMenu)
songMenu.add_command(label="Reset songs list",command=importSongs)
songMenu.add_command(label="Re-import all songs", command=reimportall)
songMenu.add_command(label="Delete song",command=deletesong)
songMenu.add_separator()
songMenu.add_command(label="Select osu! songs directory", command=getPath)

playlistMenu = Menu(menuBar)
menuBar.add_cascade(label="Playlist", menu=playlistMenu)
playlistMenu.add_command(label="New Playlist", command=createPlaylist)
playlistMenu.add_command(label="Delete Playlist", command=deletePlaylist)
playlistMenu.add_command(label="Import playlist", command=importPlaylist)

otherMenu = Menu(menuBar)
menuBar.add_cascade(label="Other", menu=otherMenu)
searchBarToggle = IntVar()
searchBarToggle.set(0)
otherMenu.add_command(label="Check for update", command=testVersion)
menuBar.add_checkbutton(label="Search Bar", variable=searchBarToggle, command=searchToggle)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#run
#load saved data
try:
    savedData = {
        "volume": open("data/volume.sav").read(),
        "shuffle": eval(open("data/shuffle.sav").read()),
        "loop": eval(open("data/loop.sav").read()),
        "kcontrol": eval(open("data/kcontrol.sav").read())
    }
except:
    os.makedirs("data")
    savedData = {
        "volume": "100",
        "shuffle": True,
        "loop": True,
        "kcontrol": True
    }
    open("data/volume.sav", 'w').write("100")
    open("data/shuffle.sav", 'w').write("True")
    open("data/loop.sav", 'w').write("True")
    open("data/kcontrol.sav", 'w').write("True")

volume.set(int(savedData["volume"]))
shuffle = savedData["shuffle"]
loop = savedData["loop"]
kcontrol = savedData["kcontrol"]

#set buttons
if not shuffle:
    shuffleButton.grid_remove()
    notShuffleButton.grid()
else:
    shuffleButton.grid()
    notShuffleButton.grid_remove()
if loop == False:
    loop2Button.grid_remove()
    notLoopButton.grid()
elif loop == True:
    notLoopButton.grid_remove()
    loopButton.grid()
elif loop == "loop":
    loopButton.grid_remove()
    loop2Button.grid()
if not kcontrol:
    kc.grid_remove()
    notKc.grid()
else:
    kc.grid()
    notKc.grid_remove()


#your osu! game directory
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

quit()

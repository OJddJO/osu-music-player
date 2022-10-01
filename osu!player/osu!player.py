from tkinter import filedialog
from pygame import mixer
from tkinter import *
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

state = "Idle"
desc = "    "

channel = None

#RPC
start = time()
clientid = '980519752025931836'
try:
    RPC = Presence(clientid)
    RPC.connect()
except:
    pass


def getPath():
    path = filedialog.askdirectory(title="Select your osu! songs directory")
    if path != "":
        open("path.data", "w").write(path)

try:
    path = open("path.data").read().replace("/", "\\")
    if not os.path.exists(path):
        getPath()
except:
    getPath()


def changeStatus():
    global run
    try:
        while run:
            global state, desc
            RPC.update(
                large_image="osu-icon-28",
                large_text="Osu!Player",
                state=state,
                details=desc,
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


def testPlaying():
    global channel, inactive_ticks, nosong, loop
    if not channel.get_busy():
        if loop:
            if state!='Paused' and state!='Idle':
                inactive_ticks += 1 
                if inactive_ticks == 1000:
                    Next()
        else:
            Stop()
    else:
        inactive_ticks = 0


def importSongs():
    temp_song=export_osu_song.export()

    for s in temp_song:
        s=s.replace("Osu/","")
        songs_list.insert(END,s)
        slist.append(s)


def reimportall():
    global slist, songs_list
    root.title("osu!player - Re-importing songs")
    path = 'import.data'
    slist = []
    songs_list.delete(0, END)
    os.remove(path)
    path2 = 'Osu\\'
    tmp = os.listdir(path2)
    for element in tmp:
        os.remove(path2+"\\"+element)
    importSongs()
    root.title("osu!player")


def deletesong():
    curr_song=songs_list.curselection()
    songs_list.delete(curr_song[0])


def Play():
    global desc, state
    if state == "Paused":
        channel.unpause()
        state = "Listening"
    else:
        channel.pause()
        channel.stop()
        song=songs_list.get(ACTIVE)
        songs_list.selection_set(slist.index(song))
        desc = song
        state = "Listening"
        song=f'Osu\\{song}'
        song = mixer.Sound(song)
        channel.play(song)
    nowplaying.set(f"{state}: {desc}")


def Pause():
    channel.pause()
    global  state
    state = "Paused"
    nowplaying.set(f"{state}: {desc}")


def Stop():
    channel.pause()
    channel.stop()
    songs_list.selection_clear(ACTIVE)
    global state, desc
    state = "Idle"
    desc = "    "
    nowplaying.set(f"{state}")


def Previous():
    channel.pause()
    channel.stop()
    global prevx, slist, shuffle
    if shuffle:
        temp2 = slist[prevx[-1]]
        previous_one = songs_list.index(prevx[-1])
        if len(prevx)!=1:
            prevx.pop()
    else:
        previous_one=songs_list.curselection()
        previous_one=previous_one[0]-1
        temp2=songs_list.get(previous_one)
    global state, desc
    state = "Listening"
    desc = temp2
    temp2=f'Osu\\{temp2}'
    song = mixer.Sound(temp2)
    channel.play(song)
    songs_list.selection_clear(0,END)
    songs_list.see(previous_one)
    songs_list.activate(previous_one)
    songs_list.selection_set(previous_one)
    nowplaying.set(f"{state}: {desc}")


def Next():
    channel.pause()
    channel.stop()
    global x, shuffle, prevx, slist
    if shuffle:
        prevx.append(slist.index(songs_list.get(ACTIVE)))
        x = randint(0, len(slist)-1)
        temp = slist[x]
        next_one = songs_list.index(x)
    else:
        next_one=songs_list.curselection()
        next_one=next_one[0]+1
        temp=songs_list.get(next_one) 
    global state, desc
    state = "Listening"
    desc = temp
    temp=f'Osu\\{temp}'
    song = mixer.Sound(temp)
    channel.play(song)
    songs_list.selection_clear(0,END)
    songs_list.see(next_one)
    songs_list.activate(next_one)
    songs_list.selection_set(next_one)
    nowplaying.set(f"{state}: {desc}")


loop = True
def Loop():
    global loop, looptxt
    if loop == True:
        loop = False
        looptxt.set("🔁:❎")
    elif loop == False:
        loop = True
        looptxt.set("🔁:✅")


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


root=Tk()
root.title('osu!player')
root.resizable(False, False)
root.config(bg="gray15")

inactive_ticks = 0
nosong = False

mixer.init()
channel = mixer.Channel(1)

songs_list=Listbox(root,selectmode=SINGLE,bg="gray15",fg="white",bd=0,highlightthickness=0,font=('arial',15),height=14,width=65,selectbackground="gray",selectforeground="black")
songs_list.grid(columnspan=8)

nowplaying=StringVar()
nowplaying.set(f"{state}")
playing_label=Label(root,textvariable=nowplaying,width=55,bg="gray15",fg="white",bd=2,highlightthickness=0,font=('arial', 13), relief='groove')
playing_label.grid(row=1, column=0, columnspan=6, pady=5)

play_button=Button(root,text="▶",width =4,command=Play)
play_button.config(font=('arial',20),bg="gray40",fg="white",bd=2,highlightthickness=0, relief='groove')
play_button.grid(row=2,column=0, padx=5)


pause_button=Button(root,text="⏸️",width =4,command=Pause)
pause_button.config(font=('arial',20),bg="gray40",fg="white",bd=2,highlightthickness=0, relief='groove')
pause_button.grid(row=2,column=1, padx=5)


stop_button=Button(root,text="⏹️",width =4,command=Stop)
stop_button.config(font=('arial',20),bg="gray40",fg="white",bd=2,highlightthickness=0, relief='groove')
stop_button.grid(row=2,column=2, padx=5)


previous_button=Button(root,text="⏮️",width =4,command=Previous)
previous_button.config(font=('arial',20),bg="gray40",fg="white",bd=2,highlightthickness=0, relief='groove')
previous_button.grid(row=2,column=3, padx=5)


next_button=Button(root,text="⏭️",width =4,command=Next)
next_button.config(font=('arial',20),bg="gray40",fg="white",bd=2,highlightthickness=0, relief='groove')
next_button.grid(row=2,column=4, padx=5)

looptxt = StringVar()
looptxt.set("🔁:✅")
loop_button=Button(root,textvariable=looptxt,width=5,command=Loop)
loop_button.config(font=('arial',20),bg="gray40",fg="white",bd=2,highlightthickness=0, relief='groove')
loop_button.grid(row=2,column=5, padx=5)

shuffletxt = StringVar()
shuffletxt.set("🔀:✅")
shuffle_button=Button(root,textvariable=shuffletxt,width=5,command=Shuffle)
shuffle_button.config(font=('arial',20),bg="gray40",fg="white",bd=2,highlightthickness=0, relief='groove')
shuffle_button.grid(row=2,column=6, padx=5)

kclabel = StringVar()
kclabel.set("⌨:✅")
def kcstate():
    global kcontrol, kclabel
    if kcontrol == True:
        kcontrol = False
        kclabel.set("⌨:❎")
    elif kcontrol == False:
        kcontrol = True
        kclabel.set("⌨:✅")

kc = Button(root,textvariable=kclabel,width=5,command=kcstate)
kc.config(font=('arial',20),bg="gray40",fg="white",bd=2,highlightthickness=0, relief='groove')
kc.grid(row=2,column=7)


voltxt = Label(root, bg="gray15", fg="white", text="Volume:")
voltxt.config(font=('arial',12),bd=0,highlightthickness=0)
voltxt.grid(row=1, column=6, pady=5)

volume = Scale(root, from_=0, to=100, orient=HORIZONTAL, variable=IntVar)
volume.grid(row=1, column=7, pady=5)
volume.config(bg="gray15", fg="white", bd=0, highlightthickness=0)
volume.set(100)

regvol = 100

def changeVol():
    global channel, regvol, volume
    regvol = int(volume.get())
    if channel.get_volume() == regvol/100:
        pass
    else:
        channel.set_volume(regvol/100)

my_menu=Menu(root)
root.config(menu=my_menu)
add_song_menu=Menu(my_menu)
my_menu.add_cascade(label="File",menu=add_song_menu)
add_song_menu.add_command(label="Import Songs From Osu!",command=importSongs)
add_song_menu.add_command(label="Re-import all songs", command=reimportall)
add_song_menu.add_command(label="Delete song",command=deletesong)
add_song_menu.add_separator()
add_song_menu.add_command(label="Select osu! songs directory", command=getPath)


def searchToggle():
    if searchBarToggle.get() == 0:
        searchValue.set("")
        searchBar.grid_remove()
        searchTxt.grid_remove()
    elif searchBarToggle.get() == 1:
        searchTxt.grid(row=3, column=0)
        searchBar.grid(row=3, column=1, columnspan=7, pady=5)

other_menu = Menu(my_menu)
my_menu.add_cascade(label="Other", menu=other_menu)
searchBarToggle = IntVar()
searchBarToggle.set(0)
other_menu.add_checkbutton(label="Search Bar", variable=searchBarToggle, command=searchToggle)

searchTxt = Label(root, bg="gray15", fg="white", text="Search:")
searchTxt.config(font=('arial',12),bd=0,highlightthickness=0)

def search(searchValue):
    songs_list.delete(0, END)
    tmp = searchValue.get()
    for element in slist:
        if tmp in element:            
            songs_list.insert(END, element)

searchValue = StringVar()
searchValue.set("")
searchValue.trace_add("write", lambda name, index, mode, sv=searchValue : search(sv))
searchBar = Entry(root, textvariable=searchValue,width=60,bg="gray15", fg="white", insertbackground="white")
searchBar.config(bg="gray15",fg="white",bd=2,highlightthickness=0,font=('arial', 13), relief='groove')


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

other_menu.add_command(label="Check for update", command=testVersion)


def shutdown():
    global run
    run = False
    root.quit()
root.protocol("WM_DELETE_WINDOW", shutdown)


importSongs()
testVersion(launch=True)

root.iconbitmap("osu-icon-28.ico")

threadA = threading.Thread(target= changeStatus)
threadA.start()


while run:
    root.update()
    testPlaying()
    changeVol()
    kinput()

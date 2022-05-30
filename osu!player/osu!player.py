from pygame import mixer
from tkinter import *
from pypresence import Presence
from time import time, sleep
import asyncio
import os
import export_osu_song
import threading

user = os.getlogin()

slist = []

state = "Idle"
desc = "    "

channel = None

#RPC
start = time()
clientid = '980519752025931836'
RPC = Presence(clientid)
RPC.connect()
run = True

def changeStatus():
    global run
    while run:
        try:
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
        if s != 'AlbumArtSmall.jpg' or s != 'Folder.jpg':
            s=s.replace(f"C:/Users/{user}/Music/osu!player/Osu/","")
            songs_list.insert(END,s)
            slist.append(s)


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
        song=f'C:/Users/{user}/Music/osu!player/Osu/{song}'
        song = mixer.Sound(song)
        channel.play(song)


def Pause():
    channel.pause()
    global  state
    state = "Paused"


def Stop():
    channel.pause()
    channel.stop()
    songs_list.selection_clear(ACTIVE)
    global state, desc
    state = "Idle"
    desc = "    "


def Previous():
    channel.pause()
    channel.stop()
    previous_one=songs_list.curselection()
    previous_one=previous_one[0]-1
    temp2=songs_list.get(previous_one)
    global state, desc
    state = "Listening"
    desc = temp2
    temp2=f'C:/Users/{user}/Music/osu!player/Osu/{temp2}'
    song = mixer.Sound(temp2)
    channel.play(song)
    songs_list.selection_clear(0,END)
    songs_list.activate(previous_one)
    songs_list.selection_set(previous_one)


def Next():
    channel.pause()
    channel.stop()
    next_one=songs_list.curselection()
    next_one=next_one[0]+1
    temp=songs_list.get(next_one) 
    global state, desc
    state = "Listening"
    desc = temp
    temp=f'C:/Users/{user}/Music/osu!player/Osu/{temp}'
    song = mixer.Sound(temp)
    channel.play(song)
    songs_list.selection_clear(0,END)
    songs_list.activate(next_one)
    songs_list.selection_set(next_one)


loop = True
def Loop():
    global loop, txt
    if loop == True:
        loop = False
        txt.set("Loop = False")
    elif loop == False:
        loop = True
        txt.set("Loop = True")


root=Tk()
root.title('osu!player')
root.resizable(False, False)

inactive_ticks = 0
nosong = False

mixer.init()
channel = mixer.Channel(1)

songs_list=Listbox(root,selectmode=SINGLE,bg="gray15",fg="white",font=('arial',15),height=12,width=66,selectbackground="gray",selectforeground="black")
songs_list.grid(columnspan=9)


play_button=Button(root,text="Play",width =7,command=Play)
play_button.config(font=('arial',15),bg="gray40",fg="white")
play_button.grid(row=1,column=0)


pause_button=Button(root,text="Pause",width =7,command=Pause)
pause_button.config(font=('arial',15),bg="gray40",fg="white")
pause_button.grid(row=1,column=1)


stop_button=Button(root,text="Stop",width =7,command=Stop)
stop_button.config(font=('arial',15),bg="gray40",fg="white")
stop_button.grid(row=1,column=2)


previous_button=Button(root,text="Prev",width =7,command=Previous)
previous_button.config(font=('arial',15),bg="gray40",fg="white")
previous_button.grid(row=1,column=3)


next_button=Button(root,text="Next",width =7,command=Next)
next_button.config(font=('arial',15),bg="gray40",fg="white")
next_button.grid(row=1,column=4)


loop_button=Button(root,text="Loop",width=7,command=Loop)
loop_button.config(font=('arial',15),bg="gray40",fg="white")
loop_button.grid(row=1,column=5)

txt = StringVar()
txt.set("Loop = True")
label = Label(root, textvariable=txt, width=12)
label.config(font=('arial',15),bg="gray40",fg="white")
label.grid(row=1, column=6)

my_menu=Menu(root)
root.config(menu=my_menu)
add_song_menu=Menu(my_menu)
my_menu.add_cascade(label="Menu",menu=add_song_menu)
add_song_menu.add_command(label="Import Songs From Osu!",command=importSongs)
add_song_menu.add_command(label="Delete song",command=deletesong)


def shutdown():
    global run
    run = False
    root.quit()
root.protocol("WM_DELETE_WINDOW", shutdown)


importSongs()

threadA = threading.Thread(target= changeStatus)
threadA.start()


while run:
    root.update()
    testPlaying()

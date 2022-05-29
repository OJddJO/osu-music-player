from pygame import mixer
from tkinter import *
from pypresence import Presence
from time import time, sleep
import os
import sys
import export_osu_song
import threading

user = os.getlogin()

state = "Idle"
desc = "   "

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
                buttons=[{"label": "Download the app", "url": "https://github.com/OJddJO/osu-music-player"}]
            )
        except:
            pass


def importSongs():
    temp_song=export_osu_song.export()

    for s in temp_song:
        if s != 'AlbumArtSmall.jpg' or s != 'Folder.jpg':
            s=s.replace(f"C:/Users/{user}/Music/osu!player/Osu/","")
            songs_list.insert(END,s)

def addsongs():
    temp_song= []
    tmp = os.listdir(f"C:/Users/{user}/Music/osu!player/Osu/")
    for song in tmp:
        if song.endswith("mp3"):
            temp_song.append(song)
    for s in temp_song:
        if s != 'AlbumArtSmall.jpg' or s != 'Folder.jpg':
            s=s.replace(f"C:/Users/{user}/Music/osu!player/Osu/")
            songs_list.insert(END,s)
   
def deletesong():
    curr_song=songs_list.curselection()
    songs_list.delete(curr_song[0])
    
    
def Play():
    song=songs_list.get(ACTIVE)
    global desc, state
    desc = song
    state = "Listening"
    song=f'C:/Users/{user}/Music/osu!player/Osu/{song}'
    mixer.music.load(song)
    mixer.music.play()


def Pause():
    mixer.music.pause()
    global  state
    state = "Paused"


def Stop():
    mixer.music.stop()
    songs_list.selection_clear(ACTIVE)
    global state, desc
    state = "Idle"
    desc = "   "


def Resume():
    mixer.music.unpause()
    global state
    state = "Listening"


def Previous():
    previous_one=songs_list.curselection()
    previous_one=previous_one[0]-1
    temp2=songs_list.get(previous_one)
    global state, desc
    state = "Listening"
    desc = temp2
    temp2=f'C:/Users/{user}/Music/osu!player/Osu/{temp2}'
    mixer.music.load(temp2)
    mixer.music.play()
    songs_list.selection_clear(0,END)
    songs_list.activate(previous_one)
    songs_list.selection_set(previous_one)

def Next():
    next_one=songs_list.curselection()
    next_one=next_one[0]+1
    temp=songs_list.get(next_one) 
    global state, desc
    state = "Listening"
    desc = temp
    temp=f'C:/Users/{user}/Music/osu!player/Osu/{temp}'
    mixer.music.load(temp)
    mixer.music.play()
    songs_list.selection_clear(0,END)
    songs_list.activate(next_one)
    songs_list.selection_set(next_one)


root=Tk()
root.title('osu!player')

mixer.init()


songs_list=Listbox(root,selectmode=SINGLE,bg="black",fg="white",font=('arial',15),height=12,width=66,selectbackground="gray",selectforeground="black")
songs_list.grid(columnspan=9)


play_button=Button(root,text="Play",width =7,command=Play)
play_button.config(font=('arial',20),bg="black",fg="white")
play_button.grid(row=1,column=0)


pause_button=Button(root,text="Pause",width =7,command=Pause)
pause_button.config(font=('arial',20),bg="black",fg="white")
pause_button.grid(row=1,column=1)


stop_button=Button(root,text="Stop",width =7,command=Stop)
stop_button.config(font=('arial',20),bg="black",fg="white")
stop_button.grid(row=1,column=2)


Resume_button=Button(root,text="Resume",width =7,command=Resume)
Resume_button.config(font=('arial',20),bg="black",fg="white")
Resume_button.grid(row=1,column=3)


previous_button=Button(root,text="Prev",width =7,command=Previous)
previous_button.config(font=('arial',20),bg="black",fg="white")
previous_button.grid(row=1,column=4)


next_button=Button(root,text="Next",width =7,command=Next)
next_button.config(font=('arial',20),bg="black",fg="white")
next_button.grid(row=1,column=5)


my_menu=Menu(root)
root.config(menu=my_menu)
add_song_menu=Menu(my_menu)
my_menu.add_cascade(label="Menu",menu=add_song_menu)
add_song_menu.add_command(label="Import Songs From Osu!",command=importSongs)
add_song_menu.add_command(label="Import Playlist",command=addsongs)
add_song_menu.add_command(label="Delete song",command=deletesong)

importSongs()

threadA = threading.Thread(target= changeStatus)
threadA.start()

mainloop()
run = False
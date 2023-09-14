class bc:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print(f"{bc.OKBLUE}[INIT]{bc.ENDC}", "Importing modules...")
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Separator
from pygame import mixer
from pypresence import Presence
from time import time
from random import randint
import os
import os.path
import export_osu_song
import osu_song_downloader
import threading
import keyboard
import requests
import webbrowser
print(f"{bc.OKBLUE}[INIT]{bc.ENDC}", "Importing modules... Done !")

class Player(Tk()):
    def __init__(self):
        super().__init__()

        #initialise variables
        self.user = os.getlogin()
        self.slist = []
        self.runVar = True
        #discord presence
        self.state = "Idle"
        self.desc = "   "
        #init variables for test playing
        self.inactiveTicks = 0
        self.noSong = False

        #load saved data
        try:
            savedData = {
                "volume": open("data/volume.sav").read(),
                "shuffle": eval(open("data/shuffle.sav").read()),
                "loop": eval(open("data/loop.sav").read()),
                "useKeyboard": eval(open("data/useKeyboard.sav").read())
            }
        except:
            print(f"{bc.OKBLUE}[INFO]{bc.ENDC}", "No saved data found, creating new one")
            os.makedirs("data")
            savedData = {
                "volume": "100",
                "shuffle": True,
                "loop": True,
                "useKeyboard": True
            }
            open("data/volume.sav", 'w').write("100")
            open("data/shuffle.sav", 'w').write("True")
            open("data/loop.sav", 'w').write("True")
            open("data/useKeyboard.sav", 'w').write("True")
        self.x = 0
        self.prevx = []
        self.regVol = 100
        self.wait = False
        self.volume.set(int(savedData["volume"]))
        self.shuffleVar = savedData["shuffle"]
        self.loopVar = savedData["loop"]
        self.useKeyboard = savedData["useKeyboard"]

        #your osu! game directory
        try:
            path = open("path.data").read().replace("/", "\\").replace("user", self.user)
            if not os.path.exists(path):
                self.getPath()
        except:
            print(f"{bc.OKBLUE}[INFO]{bc.ENDC}", "Osu! folder not found, asking user")
            self.getPath()

        #audio init
        mixer.init()
        self.channel = mixer.Channel(1)

        #tkinter init ----------------------------------------------------
        self.title("osu!player")
        self.resizable(False, False)
        self.config(bg = "gray15")

        self.songsList = Listbox(self, selectmode=SINGLE, hegigth=14, width=70)
        self.songsList.config(bg="gray15", fg="white", selectbackground="gray", selectforeground="black", bd=0, highlightthickness=0, font=('arial', 15))
        self.songsList.grid(columnspan=8)
        self.songsList.bind("<Double-Button-1>", self.playSelected)
        
        self.separator = Separator(self, orient=HORIZONTAL)
        self.separator.grid(row=1, columnspan=8, sticky="ew")

        self.nowPlaying = StringVar()
        self.nowPlaying.set(self.state)
        self.playingLabel = Label(self, textvariable=self.nowPlaying, width=60)
        self.playingLabel.config(bg="gray15", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial', 13))
        self.playingLabel.grid(row=2, columnspan=8, pady=5)

        self.playImage = PhotoImage(file="icon/play_button.png")
        self.playButton = Button(self, image=self.playImage, command=self.play)
        self.playButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
        self.playButton.grid(row=3, column=0, padx=5)

        self.pauseImage = PhotoImage(file="icon/pause_button.png")
        self.pauseButton = Button(self, image=self.pauseImage, command=self.pause)
        self.pauseButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
        self.pauseButton.grid(row=3, column=1, padx=5)

        self.stopImage = PhotoImage(file="icon/stop_button.png")
        self.stopButton = Button(self, image=self.stopImage, command=self.stop)
        self.stopButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
        self.stopButton.grid(row=3, column=2, padx=5)
        
        self.previousImage = PhotoImage(file="icon/previous_button.png")
        self.previousButton = Button(self, image=self.previousImage, command=self.previous)
        self.previousButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
        self.previousButton.grid(row=3, column=3, padx=5)
        
        self.nextImage = PhotoImage(file="icon/next_button.png")
        self.nextButton = Button(self, image=self.nextImage, command=self.next)
        self.nextButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
        self.nextButton.grid(row=3, column=4, padx=5)
        
        self.loopImage = PhotoImage(file="icon/loop_button.png")
        self.loopButton = Button(self, image=self.loopImage, command=self.loop)
        self.loopButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
        self.loopButton.grid(row=3, column=5, padx=5)
        self.notLoopImage = PhotoImage(file="icon/not_loop_button.png")
        self.notLoopButton = Button(self, image=self.notLoopImage, command=self.loop)
        self.notLoopButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
        self.notLoopButton.grid(row=3, column=5, padx=5)
        self.notLoopButton.grid_remove()
        self.loop2Image = PhotoImage(file="icon/loop2_button.png")
        self.loop2Button = Button(self, image=self.loop2Image, command=self.loop)
        self.loop2Button.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
        self.loop2Button.grid(row=3, column=5, padx=5)
        self.loop2Button.grid_remove()

        self.shuffleImage = PhotoImage(file="icon/shuffle_button.png")
        self.shuffleButton = Button(self, image=self.shuffleImage, command=self.shuffle)
        self.shuffleButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
        self.shuffleButton.grid(row=3, column=6, padx=5)
        self.notShuffleImage = PhotoImage(file="icon/not_shuffle_button.png")
        self.notShuffleButton = Button(self, image=self.notShuffleImage, command=self.shuffle)
        self.notShuffleButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
        self.notShuffleButton.grid(row=3, column=6, padx=5)
        self.notShuffleButton.grid_remove()

        self.kcImage = PhotoImage(file="icon/keyboard_button.png")
        self.kcButton = Button(self, image=self.kcImage, command=self.kc)
        self.kcButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
        self.kcButton.grid(row=3, column=7, padx=5)
        self.notKcImage = PhotoImage(file="icon/not_keyboard_button.png")
        self.notKcButton = Button(self, image=self.notKcImage, command=self.kc)
        self.notKcButton.config(bg="gray15", activebackground="gray15", highlightthickness=0, bd=0)
        self.notKcButton.grid(row=3, column=7, padx=5)
        self.notKcButton.grid_remove()

        self.volTxt = Label(self, text="Volume")
        self.volTxt.config(bg="gray15", fg="white", bd=0, highlightthickness=0, font=('arial', 13))
        self.volTxt.grid(row=2, column=6, pady=5)
        self.volume = Scale(self, from_=0, to=100, orient=HORIZONTAL, variable=IntVar)
        self.volume.config(bg="gray15", fg="white", bd=0, highlightthickness=0)
        self.volume.grid(row=2, column=7, pady=5)

        self.searchTxt = Label(self, text="Search:")
        self.searchTxt.config(bg="gray15", fg="white", bd=0, highlightthickness=0, font=('arial', 13))
        self.searchValue = StringVar()
        self.searchValue.set("")
        self.searchValue.trace_add("write", lambda name, index, mode, sv=self.searchValue: self.search(sv))
        self.searchBar = Entry(self, textvariable=self.searchValue, width=60)
        self.searchBar.config(bg="gray15", fg="white", bd=0, highlightthickness=0, font=('arial', 13))

        #menu
        self.menuBar = Menu(self)
        self.config(menu=self.menuBar)

        self.songMenu = Menu(self.menuBar)
        self.menuBar.add_cascade(label="Songs", menu=self.songMenu)
        self.songMenu.add_command(label="Import songs", command=self.importSongs)
        self.songMenu.add_command(label="Re-import all songs", command=self.reimportAll)
        self.songMenu.add_command(label="Delete song", command=self.deleteSong)
        self.songMenu.add_separator()
        self.songMenu.add_command(label="Select osu! songs directory", command=self.getPath)
        self.songMenu.add_separator()
        self.songMenu.add_command(label="Download new songs", command=self.downloadSongs)

        self.playlistMenu = Menu(self.menuBar)
        self.menuBar.add_cascade(label="Playlist", menu=self.playlistMenu)
        self.playlistMenu.add_command(label="Create playlist", command=self.createPlaylist)
        self.playlistMenu.add_command(label="Delete playlist", command=self.deletePlaylist)
        self.playlistMenu.add_command(label="Import Playlist", command=self.importPlaylist)

        self.otherMenu = Menu(self.menuBar)
        self.menuBar.add_cascade(label="Other", menu=self.otherMenu)
        self.otherMenu.add_command(label="Check for updates", command=self.testVersion)
        self.searchBarToggle = IntVar()
        self.searchBarToggle.set(0)
        self.menuBar.add_checkbutton(label="Search bar", variable=self.searchBarToggle, command=self.searchToggle)
        # ----------------------------------------------------------------

        self.discordPresence()
        self.changeStatusThread = threading.Thread(target=self.changeStatus)
        self.update()
        self.iconbitmap("osu-icon-28.ico")
        self.protocol("WM_DELETE_WINDOW", self.shutdown)


    def run(self):
        self.importSongs()
        #auto check update
        self.testVersion(launch=True)
        threading.Thread(target=self.changeStatusThread).start()
        while self.runVar:
            if not self.wait:
                self.update()
                self.testPlaying()
                self.changeVol()
                self.kinput()
        quit()


    def discordPresence(self):
        self.start = time()
        client_id = '980519752025931836'
        try:
            self.RPC = Presence(client_id)
            self.RPC.connect()
            print(f"{bc.OKBLUE}[INIT]{bc.ENDC}", "Discord RPC is ready !")
        except:
            print(f"{bc.OKBLUE}[INIT]{bc.ENDC}", "Discord not found .")


    def getPath(self):
        self.path = filedialog.askdirectory(title="Select your osu! songs directory")
        if self.path != "":
            open("path.data", "w").write(self.path)

    
    def changeStatus(self):
        try:
            while self.run:
                self.RPC.update(
                    large_image="osu-icon-28",
                    large_text="Osu!Player",
                    state=self.state,
                    details=self.desc.replace(".mp3", ""),
                    start=self.start,
                    buttons=[{"label": "Download the app", "url": "https://github.com/OJddJO/osu-music-player.exe"}]
                )
        except:
            pass
    

    def kinput(self):
        if self.useKeyboard:
            if keyboard.is_pressed('ctrl+alt+space'):
                if self.state == 'Paused' or self.state == 'Idle':
                    self.play()
                    while keyboard.is_pressed('ctrl+alt+space'):
                        ''
                elif self.state == 'Listening':
                    self.pause()
                    while keyboard.is_pressed('ctrl+alt+space'):
                        ''
            elif keyboard.is_pressed('ctrl+alt+left'):
                self.previous()
                while keyboard.is_pressed('ctrl+alt+left'):
                    ''
            elif keyboard.is_pressed('ctrl+alt+right'):
                self.next()
                while keyboard.is_pressed('ctrl+alt+right'):
                    ''
            elif keyboard.is_pressed('ctrl+alt+up'):
                self.volume.set(self.volume.get()+5)
                while keyboard.is_pressed('ctrl+alt+up'):
                    ''
            elif keyboard.is_pressed('ctrl+alt+down'):
                self.volume.set(self.volume.get()-5)
                while keyboard.is_pressed('ctrl+alt+down'):
                    ''


    def testPlaying(self):
        if not self.channel.get_busy():
            if self.loop:
                if self.state != 'Paused' and self.state != 'Idle':
                    self.inactiveTicks += 1
                    if self.inactiveTicks == 1000:
                        self.next()
            elif self.loop == 'loop':
                if self.state != 'Paused' and self.state != 'Idle':
                    self.inactiveTicks += 1
                    if self.inactiveTicks == 1000:
                        self.play()
            else:
                self.stop()
        else:
            self.inactiveTicks = 0

    
    def importSongs(self):
        print(f"{bc.OKCYAN}[INFO]{bc.ENDC}", "Importing songs...")
        self.slist = []
        self.songsList.delete(0, END)
        tmp =  export_osu_song.export()
        for song in tmp:
            song = song.eplace("Osu/", "").replace(".mp3", "")
            self.songsList.insert(END, song)
            self.slist.append(song)
        print(f"{bc.OKGREEN}[INFO]{bc.ENDC}", f"Imported {len(self.slist)} songs !")


    def reimportAll(self):
        self.title("osu!player - Re-importing songs")
        path = 'import.data'
        self.slist = []
        self.songsList.delete(0, END)
        os.remove(path)
        path2 = 'Osu/'
        tmp = os.listdir(path2)
        for song in tmp:
            os.remove(path2+song)
        self.importSongs()
        self.title("osu!player")


    def deleteSong(self):
        curr_song = self.songsList.curselection()
        self.songsList.delete(curr_song[0])


    def playSelected(self, event):
        self.channel.stop()
        song = self.songsList.get(ACTIVE)
        self.songsList.selection_set(self.slist.index(song))
        self.desc = song
        self.state = "Listening"
        song = f'Osu/{song}.mp3'
        song = mixer.Sound(song)
        self.channel.play(song)
        self.nowPlaying.set(f"{self.state}: {self.desc}")


    def play(self):
        if self.state == 'Paused':
            self.channel.unpause()
            self.state = 'Listening'
        else:
            self.channel.stop()
            song = self.songsList.get(ACTIVE)
            self.songsList.selection_set(self.slist.index(song))
            self.desc = song
            self.state = "Listening"
            song = f'Osu/{song}.mp3'
            song = mixer.Sound(song)
            self.channel.play(song)
        self.nowPlaying.set(f"{self.state}: {self.desc}")


    def pause(self):
        self.channel.pause()
        self.state = 'Paused'
        self.nowPlaying.set(f"{self.state}: {self.desc}")


    def stop(self):
        self.channel.stop()
        self.songsList.selection_clear(ACTIVE)
        self.state = 'Idle'
        self.desc = '   '
        self.nowPlaying.set(f"{self.state}: {self.desc}")


    def previous(self):
        try:
            self.channel.stop()
            if self.shuffle:
                tmp = self.slist[self.prevx[-1]]
                previousOne = self.songsList.index(self.prevx[-1])
                if len(self.prevx) != 1:
                    self.prevx.pop()
            else:
                previousOne = self.songsList.curselection()
                previousOne = previousOne[0] - 1
                if previousOne < 0:
                    previousOne = len(self.slist) - 1
                tmp = self.songsList.get(previousOne)
            self.state = "Listening"
            self.desc = tmp
            tmp = f'Osu/{tmp}.mp3'
            song = mixer.Sound(tmp)
            self.channel.play(song)
            self.songsList.selection_clear(0, END)
            self.songsList.see(previousOne)
            self.songsList.selection_set(previousOne)
            self.songsList.activate(previousOne)
            self.nowPlaying.set(f"{self.state}: {self.desc}")
        except:
            print(f"{bc.FAIL}[ERROR]{bc.ENDC}", "Can't play previous song")


    def next(self):
        try:
            self.channel.stop()
            if self.shuffle:
                self.prevx.append(self.slist.index(self.songsList.get(ACTIVE)))
                x = randint(0, len(self.slist)-1)
                while self.slist[x] in self.prevx:
                    x = randint(0, len(self.slist)-1)
                tmp = self.slist[x]
                nextOne = self.songsList.index(x)
            else:
                nextOne = self.songsList.curselection()
                nextOne = nextOne[0] + 1
                if nextOne > len(self.slist) - 1:
                    nextOne = 0
                tmp = self.songsList.get(nextOne)
            self.state = "Listening"
            self.desc = tmp
            tmp = f'Osu/{tmp}.mp3'
            song = mixer.Sound(tmp)
            self.channel.play(song)
            self.songsList.selection_clear(0, END)
            self.songsList.see(nextOne)
            self.songsList.selection_set(nextOne)
            self.songsList.activate(nextOne)
            self.nowPlaying.set(f"{self.state}: {self.desc}")
        except:
            print(f"{bc.FAIL}[ERROR]{bc.ENDC}", "Can't play next song")


    def loop(self):
        loopList = [False, True, 'loop']
        index = loopList.index(self.loopVar)-1
        if index > 2:
            index = 0
        self.loopVar = loopList[index]
        if self.loopVar == False:
            self.loop2Button.grid_remove()
            self.notLoopButton.grid()
        elif self.loopVar == True:
            self.notLoopButton.grid_remove()
            self.loopButton.grid()
        elif self.loopVar == 'loop':
            self.loopButton.grid_remove()
            self.loop2Button.grid()


    def shuffle(self):
        if self.shuffle:
            self.shuffle = False
            self.shuffleButton.grid_remove()
            self.notShuffleButton.grid()
        else:
            self.shuffle = True
            self.notShuffleButton.grid_remove()
            self.shuffleButton.grid()


    def kc(self):
        if self.useKeyboard:
            self.useKeyboard = False
            self.kcButton.grid_remove()
            self.notKcButton.grid()
        else:
            self.useKeyboard = True
            self.notKcButton.grid_remove()
            self.kcButton.grid()


    def changeVol(self):
        self.regVol = int(self.volume.get())
        if self.channel.get_volume() != self.regVol/100:
            self.channel.set_volume(self.regVol/100)


    def searchToggle(self):
        if self.searchBarToggle.get() == 1:
            self.searchTxt.grid(row=2, column=0, pady=5)
            self.searchBar.grid(row=2, column=1, pady=5)
            self.searchBar.focus_set()
        else:
            self.searchValue.set("")
            self.searchTxt.grid_remove()
            self.searchBar.grid_remove()


    def search(self, sv):
        self.songsList.delete(0, END)
        for song in self.slist:
            if sv.get().lower() in song.lower():
                self.songsList.insert(END, song)


    def versionWindow(self, update):
        def updateApp():
            webbrowser.open("https://github.com/OJddJO/osu-music-player.exe/releases/latest/")
            vWin.destroy()

        vWin = Toplevel(self)
        vWin.geometry("200x40")
        vWin.iconbitmap("osu-icon-28.ico")
        vWin.resizable(False, False)
        vWin.title("Check for updates")
        vWin.config(bg="gray15")

        txt = StringVar()
        txtUpdate = Label(vWin, textvariable=txt)
        txtUpdate.config(bg="gray15", fg="white", bd=0, highlightthickness=0)
        txtUpdate.pack()
        if update:
            txt.set("Update available !")
            updateButton = Button(vWin, text="Update", command=updateApp)
            updateButton.config(bg="gray40",fg="white",bd=2,highlightthickness=0, relief='groove')
            updateButton.pack()
        else:
            txt.set("You have the latest version !")

        def shutdown():
            vWin.destroy()
        vWin.protocol("WM_DELETE_WINDOW", shutdown)
        threading.Thread(target=vWin.mainloop).start()


    def testVersion(self, launch=False):
        try:
            version = requests.get("https://api.github.com/repos/OJddJO/osu-music-player.exe/releases/latest").json()["tag_name"]
            if version != open("version.txt").read():
                self.versionWindow(True)
            else:
                print(f"{bc.OKBLUE}[INFO]{bc.ENDC}", "You have the latest version !")
                if launch:
                    print(f"{bc.WARNING}[WARNING]{bc.ENDC}", "Update available !")
                    self.versionWindow(False)
        except:
            print(f"{bc.FAIL}[ERROR]{bc.ENDC}", "Can't check for updates !")


    def createPlaylist(self):
        def create():
            if playlistName.get() != "":
                songs = self.songsList.curselection()
                songsFile = []
                for index in songs:
                    songsFile.append(self.slist[index])
                open(f"playlists/{playlistName.get()}.txt", 'w').write(str(songsFile))
                pWin.destroy()
            else:
                print(f"{bc.FAIL}[ERROR]{bc.ENDC}", "Playlist name can't be empty !")

        def shutdown():
            pWin.destroy()

        try:
            os.listdir("playlists")
        except:
            print(f"{bc.OKCYAN}[INFO]{bc.ENDC}", "Creating playlists directory...", end=" ")
            os.mkdir("playlists")
            print("Done !")

        pWin = Toplevel(self)
        pWin.iconbitmap("osu-icon-28.ico")
        pWin.resizable(False, False)
        pWin.title("Create playlist")
        pWin.config(bg="gray15")
        pWin.protocol("WM_DELETE_WINDOW", shutdown)

        songsList=Listbox(pWin, selectmode=MULTIPLE, height=14, width=50)
        songsList.config(bg="gray15", fg="white", selectbackground="gray", selectforeground="black", bd=0, highlightthickness=0, font=('arial', 15))
        songsList.grid(columnspan=8)

        playlistLabel = Label(pWin, text="Name :")
        playlistLabel.config(bg="gray15", fg="white", bd=0, highlightthickness=0)
        playlistLabel.grid(row=1, column=0, pady=5)

        playlistName = StringVar()
        playlistName.set("")
        playlistNameEntry = Entry(pWin, textvariable=playlistName, width=40, justify='center')
        playlistNameEntry.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
        playlistNameEntry.grid(row=1, column=1, columnspan=5, pady=5)

        createButton = Button(pWin, text="Create", command=create)
        createButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
        createButton.grid(row=1, column=6, pady=5)

        cancelButton = Button(pWin, text="Cancel", command=shutdown)
        cancelButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
        cancelButton.grid(row=1, column=7, pady=5)

        temp_song=export_osu_song.export()

        for s in temp_song:
            s=s.replace("Osu/","").replace(".mp3","")
            songsList.insert(END,s)
            self.slist.append(s)
        threading.Thread(target=pWin.mainloop).start()


    def importPlaylist(self):
        def usePlaylist():
            slistCopy = self.slist.copy()
            self.slist = []
            i = playlistListbox.curselection()[0]
            playlistNameVar.set(playlistPath[i])
            songs = eval(open(f"playlists/{playlistPath[i]}").read())
            try:
                for song in songs:
                    self.slist.append(song)
                    self.songsList.insert(END, song)
            except:
                try:
                    for song in songs:
                        if song in slistCopy:
                            self.slist.append(song)
                            self.songsList.insert(END, song)
                        else:
                            print(f"{bc.FAIL}[ERROR]{bc.ENDC}", f"{song} not found !")
                            print(f"{bc.FAIL}[ERROR]{bc.ENDC}", "Removing it from the playlist...", end=" ")
                            songs.remove(song)
                            print("Done !")
                except:
                    print(f"{bc.FAIL}[ERROR]{bc.ENDC}", "Can't import playlist !")
            #save playlist
            open(f"playlists/{playlistPath[i]}", 'w').write(str(songs))

        def changePlaylistName():
            try:
                i = playlistListbox.curselection()[0]
                playlistNameVar.set(playlistPath[i])
            except:
                pass

        def shutdown():
            pWin.destroy()
            
        pWin = Toplevel(self)
        pWin.iconbitmap("osu-icon-28.ico")
        pWin.config(bg="gray15")
        pWin.title("Import a playlist")
        pWin.resizable(False, False)
        pWin.protocol("WM_DELETE_WINDOW", shutdown)

        playlistListbox = Listbox(pWin, selectmode=SINGLE, height=14, width=50)
        playlistListbox.config(bg="gray15", fg="white", selectbackground="gray", selectforeground="black", bd=0, highlightthickness=0, font=('arial', 15))
        playlistListbox.grid(columnspan=8)
        playlistListbox.bind("<Double-Button-1>", lambda args: usePlaylist())
        playlistListbox.bind("<Button-1>", lambda args: changePlaylistName())

        playlistLabel = Label(pWin, text="Selected:")
        playlistLabel.config(bg="gray15", fg="white", bd=0, highlightthickness=0)
        playlistLabel.grid(row=1, column=0, pady=5)

        playlistNameVar = StringVar()
        playlistNameVar.set("")
        playlistNameLabel = Label(pWin, textvariable=playlistNameVar, width=40, justify='center')
        playlistNameLabel.config(bg="gray15", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial', 13))
        playlistNameLabel.grid(row=1, column=1, columnspan=5, pady=5)

        useButton = Button(pWin, text="Select", command=usePlaylist)
        useButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
        useButton.grid(row=1, column=6, pady=5)

        cancelButton = Button(pWin, text="Cancel", command=shutdown)
        cancelButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
        cancelButton.grid(row=1, column=7, pady=5)

        playlistPath = []
        for element in os.listdir("playlists"):
            if element.endswith(".txt"):
                playlistPath.append(element)
                playlistName = element.replace(".txt", "")
                playlistListbox.insert(END, playlistName)
        threading.Thread(target=pWin.mainloop).start()


    def deletePlaylist(self):
        def shutdown():
            pWin.destroy()

        def delete():
            try:
                i = playlistListbox.curselection()[0]
                os.remove(f"playlists/{playlistPath[i]}")
                pWin.destroy()
            except:
                print(f"{bc.FAIL}[ERROR]{bc.ENDC}", "Can't delete playlist")

        def changePlaylistName():
            try:
                i = playlistListbox.curselection()[0]
                playlistNameVar.set(playlistPath[i])
            except:
                pass

        pWin = Toplevel(self)
        pWin.iconbitmap("osu-icon-28.ico")
        pWin.config(bg="gray15")
        pWin.title("Delete a playlist")
        pWin.resizable(False, False)
        pWin.protocol("WM_DELETE_WINDOW", shutdown)

        playlistListbox = Listbox(pWin, selectmode=SINGLE, height=14, width=50)
        playlistListbox.config(bg="gray15", fg="white", selectbackground="gray", selectforeground="black", bd=0, highlightthickness=0, font=('arial', 15))
        playlistListbox.grid(columnspan=8)
        playlistListbox.bind("<Double-Button-1>", lambda args: delete())
        playlistListbox.bind("<Button-1>", lambda args: changePlaylistName())

        playlistLabel = Label(pWin, text="Name:")
        playlistLabel.config(bg="gray15", fg="white", bd=0, highlightthickness=0)
        playlistLabel.grid(row=1, column=0, pady=5)

        playlistNameVar = StringVar()
        playlistNameVar.set("")
        playlistNameLabel = Label(pWin, textvariable=playlistNameVar, width=40, justify='center')
        playlistNameLabel.config(bg="gray15", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial', 13))
        playlistNameLabel.grid(row=1, column=1, columnspan=5, pady=5)

        deleteButton = Button(pWin, text="Delete", command=delete)
        deleteButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
        deleteButton.grid(row=1, column=6, pady=5)

        cancelButton = Button(pWin, text="Cancel", command=shutdown)
        cancelButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
        cancelButton.grid(row=1, column=7, pady=5)

        playlistPath = []
        for element in os.listdir("playlists"):
            if element.endswith(".txt"):
                playlistPath.append(element)
                playlistName = element.replace(".txt", "")
                playlistListbox.insert(END, playlistName)
        threading.Thread(target=pWin.mainloop).start()


    def playlistAddSong(self):
        def shutdown():
            pWin.destroy()

        def addSong():
            try:
                i = playlistListbox.curselection()[0]
                songs = eval(open(f"playlists/{playlistPath[i]}").read())
                for songs in songListbox.curselection():
                    songs.append(slist[songs])
                open(f"playlists/{playlistPath[i]}", 'w').write(str(songs))
                pWin.destroy()
            except:
                print(f"{bc.FAIL}[ERROR]{bc.ENDC}", "Can't add song")

        def changePlaylistName():
            try:
                i = playlistListbox.curselection()[0]
                playlistNameVar.set(playlistPath[i])
            except:
                pass

        pWin = Toplevel(self)
        pWin.iconbitmap("osu-icon-28.ico")
        pWin.config(bg="gray15")
        pWin.title("Delete a playlist")
        pWin.resizable(False, False)
        pWin.protocol("WM_DELETE_WINDOW", shutdown)

        playlistListbox = Listbox(pWin, selectmode=SINGLE, height=4, width=50)
        playlistListbox.config(bg="gray15", fg="white", selectbackground="gray", selectforeground="black", bd=0, highlightthickness=0, font=('arial', 15))
        playlistListbox.grid(columnspan=8, row=0, column=0)
        playlistListbox.bind("<Button-1>", changePlaylistName)

        self.importSongs()
        songListbox = Listbox(pWin, selectmode=MULTIPLE, height=10, width=50)
        songListbox.config(bg="gray15", fg="white", selectbackground="gray", selectforeground="black", bd=0, highlightthickness=0, font=('arial', 15))
        songListbox.grid(columnspan=8, row=1, column=0)
        slist = self.slist.copy()
        for song in slist:
            songListbox.insert(END, song)
        
        playlistLabel = Label(pWin, text="Name:")
        playlistLabel.config(bg="gray15", fg="white", bd=0, highlightthickness=0)
        playlistLabel.grid(row=2, column=0, pady=5)

        playlistNameVar = StringVar()
        playlistNameVar.set("")
        playlistNameLabel = Label(pWin, textvariable=playlistNameVar, width=40, justify='center')
        playlistNameLabel.config(bg="gray15", fg="white", bd=2, highlightthickness=0, relief='groove', font=('arial', 13))
        playlistNameLabel.grid(row=2, column=1, columnspan=5, pady=5)

        addButton = Button(pWin, text="Add", command=addSong)
        addButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
        addButton.grid(row=2, column=6, pady=5)

        cancelButton = Button(pWin, text="Cancel", command=shutdown)
        cancelButton.config(bg="gray40", fg="white", bd=2, highlightthickness=0, relief='groove')
        cancelButton.grid(row=2, column=7, pady=5)

        playlistPath = []
        for element in os.listdir("playlists"):
            if element.endswith(".txt"):
                playlistPath.append(element)
                playlistName = element.replace(".txt", "")
                playlistListbox.insert(END, playlistName)

        threading.Thread(target=pWin.mainloop).start()


    def downloadSongs(self):
        #disable tk window
        self.wait = True
        self.menuBar.entryconfig(1, state=DISABLED)
        self.menuBar.entryconfig(2, state=DISABLED)
        self.menuBar.entryconfig(3, state=DISABLED)
        self.menuBar.entryconfig(4, state=DISABLED)

        self.title("osu!player - Downloading songs")
        osu_song_downloader.Downloader().run()
        try:
            os.rmdir("temp")
        except:
            print(f"{bc.FAIL}[ERROR]{bc.ENDC}", "Can't delete temp folder")
        self.importSongs()
        self.title("osu!player")

        #enable tk window
        self.menuBar.entryconfig(1, state=NORMAL)
        self.menuBar.entryconfig(2, state=NORMAL)
        self.menuBar.entryconfig(3, state=NORMAL)
        self.menuBar.entryconfig(4, state=NORMAL)
        self.wait = False


    def shutdown(self):
        #save data to files
        open("data/volume.sav", 'w').write(str(int(self.volume.get())))
        open("data/shuffle.sav", 'w').write(str(self.shuffleVar))
        open("data/loop.sav", 'w').write(str(self.loopVar))
        open("data/kcontrol.sav", 'w').write(str(self.useKeyboard))
        self.run = False
        self.quit()


if __name__ == "__main__":
    app = Player()
    app.run()
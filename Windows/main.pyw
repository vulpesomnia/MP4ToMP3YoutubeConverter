# © 2024 Tommy Kroon <somnic.vulpes@gmail.com>

"""
Windows Version of MP4 to MP3 Youtube Converter
"""

from __future__ import unicode_literals
from tkinter import *
from tkinter import ttk
from pathlib import Path
import yt_dlp, subprocess, threading, os


appInfo = "Welcome to the MP4 to MP3 Youtube converter!\nJust input a Youtube URL in the text box above and\nlet the magic happen!"

downloadProgress = ""
isDownloading = False
audioQueue = []#
currentQueueObject = None

errorWindow = None
queueObjectHeight = 41

class queueObject():
    def __init__(self, url):
        self.frame = ttk.Frame(listFrame, width=175, height=queueObjectHeight, borderwidth=1, relief='solid')
        self.url = url
        self.name = StringVar(value=url)
        self.nameLabel = ttk.Label(self.frame, textvariable=self.name)
        self.nameLabel.place(x=0,y=0)
        self.progress = StringVar(value="In Queue")
        self.progressText = ttk.Label(self.frame, textvariable=self.progress)
        self.progressText.place(x=0,y=20)


    def updatePlacement(self, index):
        self.frame.place(x=0, y=queueObjectHeight*index)

    def updateRender(self, title):
        self.progress.set(downloadProgress)
        self.name.set(title)

def openOutputDirectory():
    if os.name == "nt":#OS is Windows:
        path = str(Path().absolute()) + "\Output"
        subprocess.run(["explorer", path])
    else:
        subprocess.run(["open-xdg", "Output"])

def progressHook(d):
    global downloadProgress, currentQueueObject
    infoDict = d['info_dict']
    if d['status'] == "downloading":
        downloadProgress = "( " + str(round(d['downloaded_bytes']/1000000, 1)) + "Mb / " + str(round(d['total_bytes']/1000000, 1)) + "Mb )"
        if infoDict['playlist'] != None:
            downloadProgress = downloadProgress + " [" + str(infoDict['playlist_index']+1) + "/" + str(infoDict['playlist_count']) + "]"
        currentQueueObject.updateRender(infoDict['fulltitle'])




def startDownloadLoop():
    global isDownloading
    if (isDownloading == False) and (len(audioQueue) > 0):
        isDownloading = True
        t1 = threading.Thread(target=downloadAudio, args=(audioQueue[0],))
        t1.start()




def downloadAudio(object):
    global currentQueueObject, isDownloading
    link = object.url
    currentQueueObject = object
    ydl_opts = {
       'format': 'bestaudio/best',
       'postprocessors': [{
           'key': 'FFmpegExtractAudio',
           'preferredcodec': 'mp3',
           'preferredquality': '192',
       }],
       'paths': {
            'home': './Output'
       },
       'ffmpeg_location': './FFmpeg-binaries/ffmpeg.exe',
       'outtmpl': "./%(title)s", 
       'progress_hooks': [progressHook]
       
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
    audioQueue.pop(0)
    currentQueueObject.frame.destroy() 
    for index, object in enumerate(audioQueue):
        object.updatePlacement(index)
    isDownloading = False
    startDownloadLoop()

def addToQueue():
    _url = queueEntry.get()
    if isEligibleURL(_url):
        queueEntry.delete(0, 'end')
        object = queueObject(_url)
        audioQueue.append(object)
        object.updatePlacement(len(audioQueue)-1)
        startDownloadLoop()


#Check if its an eligible youtube URL
def isEligibleURL(url):
    if ("youtube.com" in url) or ("youtu.be" in url):
        return True
    else:
        sendError(1, "Inserted link is not from youtube.com!")
        return False

def sendError(id, error):
    global errorWindow
    if errorWindow != None:
        errorWindow.destroy()

    errorTitle = " Error: " + str(id)
    errorWindow = Toplevel(root)
    errorWindow.title(errorTitle)
    errorWindow.geometry("300x150")
    errorWindow.resizable(0, 0)
    frame = ttk.Frame(errorWindow, borderwidth=2, relief='sunken')
    frame.pack_propagate(0)
    frame.pack(fill='both', expand=1)


    errorLabel = ttk.Label(frame, text=error)
    errorButton = ttk.Button(frame, text="Close", width=25, command=errorWindow.destroy)
    errorLabel.place(relx=0.5, rely=0.5, anchor=CENTER)
    errorButton.place(relx=0.5, rely=0.7, anchor=CENTER)


root = Tk(className=" Video to Audio (MP4toMP3 Converter)")
#main window
try:
    root.geometry("750x300")
    root.resizable(0, 0)

    Lframe = ttk.Frame(root, width=375, height=300, borderwidth=2, relief='sunken')
    Lframe.pack_propagate(0)
    Lframe.place(relx=0, rely= 0.5, anchor=W)


    infoLabel = ttk.Label(Lframe, text=appInfo, font=("Arial", 12))
    infoLabel.place(relx=0.5,rely=0.6,anchor=CENTER)

    toQueue = StringVar()
    queueEntry = ttk.Entry(Lframe, textvariable=toQueue, width=25)
    queueEntry.insert(0, "Insert URL")
    queueEntry.place(relx=0.5,rely=0.2,anchor=CENTER)

    queueButton = ttk.Button(Lframe, text="Add to Queue", width=25, command=addToQueue)
    queueButton.place(relx=0.5,rely=0.3,anchor=CENTER)

    Rframe = ttk.Frame(root, width=375, height=300, borderwidth=2, relief='sunken')
    Rframe.pack_propagate(0)
    Rframe.place(relx=1, rely= 0.5, anchor=E)

    listFrame = ttk.Frame(Rframe, width=200, height=300, borderwidth=2, relief='raised')
    listFrame.place(relx=0, rely=0)
    listFrame.pack_propagate(0)

    outputButton = ttk.Button(Rframe, text="View Output Folder", width=25, command=openOutputDirectory)
    outputButton.place(x= 205, y = 10)

    visualAudioQueue = StringVar()

    root.mainloop()
except Exception as ex:
    print("Error Occurred: \n")
    print(ex)
    input()


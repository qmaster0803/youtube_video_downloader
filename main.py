import time
from pytube import YouTube
from pytube import Playlist
import pytube.exceptions
import os
import getpass
import urllib
import sys

def queryYN(question):
    while(True):
        inp = input(question+" ")
        try:
            if(inp.split()[0] == "Y" or inp.split()[0] == "y"):
                return True
            if(inp.split()[0] == "N" or inp.split()[0] == "n"):
                return False
        except IndexError:
            return True

def showStreamSelector(video, calcMaxRes=False):
    print("Choose stream:")
    streams = []
    i = 0
    max_res = 0
    for stream in video.streams:
        if(stream.mime_type == "video/mp4" and stream.is_progressive == False):
            i += 1
            print(str(i)+") Video;", "Resolution: "+stream.resolution, "Framerate: "+str(stream.fps))
            streams.append(stream)
            if(int(stream.resolution[:-1]) > max_res): max_res = int(stream.resolution[:-1])
        if(stream.mime_type == "audio/mp4" and stream.is_progressive == False):
            i += 1
            streams.append(stream)
            print(str(i)+") Audio;", "Bitrate: "+stream.abr)
    #Requesting user's choise
    stream_num = 0
    while(True):
        try:
            stream_num = int(input("Enter number: "))-1
            if(stream_num >= 0 and stream_num <= len(streams)-1):
                break
        except ValueError:
            print("Not a number!")
    if(calcMaxRes): return streams[stream_num], max_res
    else: return streams[stream_num]

#Initializing settings
IDM_mode = True
autocopy = False

if(queryYN("Start download with IDM? [Y/n]")):
    from downloader import IDMan
    downloader = IDMan()
else: IDM_mode = False

if(not IDM_mode):
    if(queryYN("Autocopy links to clipboard? [Y/n]")):
        import pyperclip
        autocopy = True

#Welcome message and url request
print("YouTube video downloader v1.2")
url = input("Enter url to video or playlist: ")

parsed = urllib.parse.urlparse(url)
playlist = False

if(parsed.path == "/playlist"):
    print("Got playlist, processing...")
    playlist = True
if(parsed.path == "/watch" or parsed.netloc == "youtu.be"):
    print("Got video, processing...")

if(playlist):
	#playlist info
    print()
    playlist = Playlist(url)
    print("Got", len(playlist), "videos")
    print("Parsing video params, it can take long time")
    all_videos = []
    #Getting info about all videos and saving it to all_videos list
    try:
        for i, vid in enumerate(playlist.videos):
            print(str(i+1)+"/"+str(len(playlist)))
            all_videos.append(vid)
    except pytube.exceptions.VideoRegionBlocked:
        print("Sorry, blocked in your region. Try changing VPN server.")
        sys.exit(0)

    #print first video streams; progressive (audio&video in one file) isn't shown
    print("Warning! Streams listed for first video; if other videos in playlist has better quality streams, we'll notify you.")

    stream, max_res = showStreamSelector(all_videos[0], True)

    #Checks all videos for selected stream; if max quality chosen, check if other videos in playlist has better quality.
    print("Stream type got; Checking all videos.")
    if(max_res == int(stream.resolution[:-1])):
        for vid in all_videos:
            max_res2 = 0
            for stream2 in vid.streams:
                if(stream2.mime_type == "video/mp4"):
                    if(int(stream2.resolution[:-1]) > max_res2): max_res2 = int(stream2.resolution[:-1])
            if(max_res2 > max_res):
                reselect = queryYN("Video "+vid.title+" has stream with better quality, than first video in playlist. Do you want to select another stream for this video?[Y/n]")
                if(reselect):
                    stream3 = showStreamSelector(vid)
                    print(stream3.resolution, stream3.fps)

    input("waiting")
    extension = ".mp3" 

    for vid in playlist.videos:
        print("Downloading", vid.title)
        url = vid.streams.filter(type="audio")[0].url
        if(IDM_mode):
            downloader.download(url, os.getcwd(), output=vid.title+extension, lflag=5)
            idm_folder_name = urllib.parse.urlparse(url).netloc.split(".")[0]
            found = True
            while(found):
                found = False
                dirlist = os.listdir(os.path.join(os.getenv('APPDATA'), "IDM\\DwnlData\\", getpass.getuser()))
                for i in dirlist:
                    if(i[:len(idm_folder_name)] == idm_folder_name):
                        found = True
            print("Done\n")
        else:
            print("Link generated. Please paste it to your browser or other downloader.")
            print(url)
            print("\n"*5)

else:
    extension = ".mp3"
    vid = YouTube(url)
    print("Downloading", vid.title)

    print("Choose stream:")
    streams = []
    i = 0
    for stream in vid.streams:
        if(stream.mime_type == "video/mp4"):
            i += 1
            print(str(i)+") Video;", "Resolution: "+stream.resolution, "Framerate: "+str(stream.fps))
            streams.append(stream)
        if(stream.mime_type == "audio/mp4"):
            i += 1
            streams.append(stream)
            print(str(i)+") Audio;", "Bitrate: "+stream.abr)

    stream = 0
    while(True):
        try:
            stream = int(input("Enter number: "))
            if(stream >= 1 and stream <= len(streams)):
                break
        except ValueError:
            print("Not a number!")
    
    url = streams[stream-1].url
    if(streams[stream-1].type == "video"): extension = ".mp4"
    if(streams[stream-1].type == "audio"): extension = ".mp3"
    downloader.download(url, os.getcwd(), output=vid.title+extension, lflag=5)
    idm_folder_name = urllib.parse.urlparse(url).netloc.split(".")[0]
    found = True
    while(found):
        found = False
        dirlist = os.listdir(os.path.join(os.getenv('APPDATA'), "IDM\\DwnlData\\", getpass.getuser()))
        for i in dirlist:
            if(i[:len(idm_folder_name)] == idm_folder_name):
                found = True
    print("Done\n")
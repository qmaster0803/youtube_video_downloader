from selenium import webdriver
from bs4 import BeautifulSoup as BS
import time
from pytube import YouTube
from downloader import IDMan
import os
import getpass
import urllib

print("YouTube video downloader v1.0")
url = input("Enter url to video or playlist: ")

parsed = urllib.parse.urlparse(url)
playlist = False

if(parsed.path == "/playlist"):
    print("Got playlist, processing...")
    playlist = True
if(parsed.path == "/watch"):
    print("Got video, processing...")

#"https://www.youtube.com/playlist?list=PLnOLSfzhP-CfMDy-46DPdyR7IrE0BwR9P"

driver = webdriver.Chrome()
downloader = IDMan()
driver.get(url+'asd')
time.sleep(3)
html = driver.page_source
driver.close()
if(playlist):
    print("\n"*50)
    print("Playlist parsed")
    soup = BS(html, "html.parser")
    videos = soup.find_all("ytd-playlist-video-renderer",{"class": "ytd-playlist-video-list-renderer"})
    links_to_vids = []

    for video in videos:
        a = video.find("a", {"id": "video-title"})
        link = "https://www.youtube.com/" + a.get("href") 
        links_to_vids.append(link)

    print("Got", len(links_to_vids), "videos\n")

    extension = ".mp3"

    for link in links_to_vids:
        vid = YouTube(link)
        print("Downloading", vid.title)
        url = vid.streams.filter(type="audio")[0].url
        downloader.download(url, os.getcwd(), output=vid.title+extension, lflag=5)
        idm_folder_name = urllib.parse.urlparse(url).netloc.replace(".", "_")
        found = True
        while(found):
            found = False
            dirlist = os.listdir(os.path.join(os.getenv('APPDATA'), "IDM\\DwnlData\\", getpass.getuser()))
            for i in dirlist:
                if(i[:len(idm_folder_name)] == idm_folder_name):
                    found = True
        print("Done\n")
else
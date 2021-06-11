import ui_utils
import download_utils
from pytube import YouTube, Playlist

def process(url, media_type, wget_mode, autocopy):
    playlist = Playlist(url)
    if(len(playlist) == 1):
        print("Got 1 video")
    else:
        print("Got", len(playlist), "videos")

    videos = []
    for i, vid in enumerate(playlist.videos):
        videos.append(vid)
        if(i != 0): print(" "*50+"\r", end='')
        print(str(i+1)+"/"+str(len(playlist)), end='')
    print()
    print("Video data parsed.")
    print("Streams are showed for first video. If there are better quality in other videos, it will be shown on next step.")
    stream, audio_stream, selected_codec_type = ui_utils.showStreamSelector(videos[0], media_type=media_type)
    audio_mode = False
    if(selected_codec_type < 0):
        audio_mode = True
    else:
        selected_resolution = int(stream.resolution[:-1])
        selected_fps = stream.fps
    #print("res", selected_resolution)
    #print("fps", selected_fps)

    auto_largest = False
    toDownload = []
    if(not audio_mode):
        max_res_selected = False
        if(download_utils.calcMaxRes(videos[0], media_type=media_type) == selected_resolution): max_res_selected = True
        print("Max res selected", max_res_selected)
        streams_to_download = [[stream, audio_stream]]

        if(max_res_selected):
            for vid in videos:
                max_res = calcMaxRes(vid, media_type=media_type)
                if(max_res > selected_resolution):
                    auto_largest = queryYN("You've selected max resolution stream, but one of videos has larger resolution. Do you want do donwload max resolution for all videos? [Y/n]")
                    break

        for i, vid in enumerate(videos):
            print("Processing video", i+1, "from", len(videos))
            if(auto_largest): toDownload.append([download_utils.findStreams(vid, download_utils.calcMaxRes(vid, media_type=media_type), selected_fps, media_type), vid.title])
            else: toDownload.append([download_utils.findStreams(vid, selected_resolution, selected_fps, media_type), vid.title])

        if(media_type == 1):
            video_extenstion = ".mp4"
            audio_extension = ".mp3"
        if(media_type == 2):
            video_extension = ".webm"
            audio_extension = ".ogg"

        for vid in toDownload:
            download_utils.doOutput(vid[0][0].url, video_extension, vid[0][1].url, audio_extension, vid[1], wget_mode, autocopy)
    else:
        for i, vid in enumerate(videos):
            print("Processing video", i+1, "from", len(videos))
            toDownload.append([download_utils.selectAudioForVideo(vid, media_type, audio_mode=True), vid.title])

        if(media_type == 1): audio_extension = ".mp3"
        if(media_type == 2): audio_extension = ".ogg"

        for vid in toDownload:
            print("Downloading audio for ", vid[1], "...", end='', flush=True)
            download_utils.downloadFile(vid[0].url, vid[1]+audio_extension, wget_mode, autocopy)
            if(wget_mode): print("done.")
import wget

#automatically select audio stream for video stream
def selectAudioForVideo(vid, video_stream):
    video_codec = video_stream.parse_codecs()[0].split(".")[0]
    audio_stream = None
    if(video_codec == "avc1" or video_codec == "av01"): preferred_audio_codec = "mp4a"
    if(video_codec == "vp9"): preferred_audio_codec = "opus"
    print("Preff audio:", preferred_audio_codec)
    for stream in vid.streams:
        if(stream.type == "audio" and stream.parse_codecs()[1].split(".")[0] == preferred_audio_codec):
            audio_stream = stream
    return audio_stream

#return max res for video (check all streams)
def calcMaxRes(video, media_type=3):
    max_res = 0
    for stream in video.streams:
        if(stream.type == "video"):
            video_codec = stream.parse_codecs()[0].split(".")[0]
            if(media_type == 3 or (media_type == 2 and video_codec == "vp9") or (media_type == 1 and (video_codec == "avc1" or video_codec == "av01"))):
                if(int(stream.resolution[:-1]) > max_res): max_res = int(stream.resolution[:-1])
    return max_res

#select audio and video streams with selected params
def findStreams(video, res, fps, media_type):
    output_video_stream = None
    output_audio_stream = None
    for stream in video.streams:
        if(stream.type == "video" and stream.is_progressive == False):
            video_codec = stream.parse_codecs()[0].split(".")[0]
            show_stream = False
            if(media_type == 1 and (video_codec == "avc1" or video_codec == "av01")): show_stream = True
            if(media_type == 2 and video_codec == "vp9"): show_stream = True
            if(media_type == 3): show_stream = True
            if(show_stream and int(stream.resolution[:-1]) == res and stream.fps == fps): output_video_stream = stream
    output_audio_stream = selectAudioForVideo(video, output_video_stream)
    return output_video_stream, output_audio_stream

def downloadFile(url, name, wget_mode, autocopy):
    if(wget_mode):
        wget.download(url, out=name)
    else:
        if(autocopy):
            print("Link generated and copied to clipboard. Please save it with", os.path.splitext(name)[1], "extension.")
            pyperclip.copy(url)
        else:
            print("Link generated. Please save it with", os.path.splitext(name)[1], "extension.")
            print("-"*20)
            print(url)
            print("-"*20)

def doOutput(video_url, video_extension, audio_url, audio_extension, wget_mode, autocopy):
    if(wget_mode):
        print("Downloading video... ", end='', flush=True)
        downloadFile(video_url, "temp"+video_extension, wget_mode, autocopy)
        print("done.", flush=True)
        print("Downloading audio... ", end='', flush=True)
        downloadFile(audio_url, "temp"+audio_extension, wget_mode, autocopy)
        print("done.")
        print("Merging streams... ", end='', flush=True)
        mergeStreams("temp"+video_extension, "temp"+audio_extension, vid.title+video_extension)
        print("done.")
    else:
        downloadFile(video_url, "temp"+video_extension, wget_mode, autocopy)
        input("Press enter to generate next link.")
        downloadFile(audio_url, "temp"+audio_extension, wget_mode, autocopy)  
        doMerge = ui_utils.queryYN("Do you want to merge audio and video? [Y/n]")
        if(doMerge):
            input("Save audio as temp"+audio_extension+" and video as temp"+video_extension+" than press enter.")
            mergeStreams("temp"+video_extension, "temp"+audio_extension, vid.title+video_extension)
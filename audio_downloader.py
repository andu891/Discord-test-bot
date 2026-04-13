
from yt_dlp import YoutubeDL
import logging
def download_audio(url):
    url = [url]
    id = url[0][-11:]
    print(id)

    yl_opts= {
        "format":"m4a/bestaudio/best",
        "paths":{"home":f"./sound/songs/{id}"}, # folder where the file will be downloaded to 
        "postprocessors":[{ # audio processor (FFmpeg) 
            "key":"FFmpegExtractAudio",
            "preferredcodec":"m4a"
        }],
        "ffmpeg_location":"./sound/ffmpeg/bin", # audio processor location
        "windowsfilenames":True,
        #"logger": logging.getLogger()
    }

    with YoutubeDL(yl_opts) as ydl: # download from the link
        ydl.download(url)

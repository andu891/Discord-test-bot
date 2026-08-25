from yt_dlp import YoutubeDL



async def download_audio(url):
    url = [url]
    id = url[0][-11:]
    print(id)
    yl_opts= {
        "format":"m4a/bestaudio/best",
        "paths":{"home":f"./sound/{id}"}, # folder where the file will be downloaded to 
        "postprocessors":[{ # audio processor (FFmpeg) 
            "key":"FFmpegExtractAudio"
        }],
        "windowsfilenames":True,
        "cookiesfrombrowser":("firefox",), # extracts cookies from browser
        "extractor_args":{
            "youtube":{
                "player_client":["default","web_embedded"]
            }
        },
        "remote_components":["ejs:github"] # fix for youtube challenges

    }

    with YoutubeDL(yl_opts) as ydl: # download from the link
        try:
            ydl.download(url)
        except:
            return LookupError
    return 



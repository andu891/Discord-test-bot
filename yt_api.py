import os
from dotenv import load_dotenv
import requests

load_dotenv()
key = os.getenv("YOUTUBE_TOKEN")

def search(name:str) -> str:
    link = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part":"snippet",
        "q":name + "song",
        "max_results":1,
        "type":"video",
        "key":key,
        "videoDuration":"medium"
    }

    response = requests.get(url=link,params=params)
    print(response.status_code)
    response.raise_for_status()
    data = response.json()
    id= data["items"][0]["id"]["videoId"]
    return id
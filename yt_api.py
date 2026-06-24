import os
from dotenv import load_dotenv
import requests


load_dotenv()
key = os.getenv("YOUTUBE_TOKEN")




def search(name:str) -> str:
    link = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part":"snippet",
        "q":name + " song",
        "max_results":1,
        "type":"video",
        "key":key,
        "videoDuration":"medium"
    }

    response = requests.get(url=link,params=params)
    print(response.status_code)
    print(response.reason)
    
    response.raise_for_status()
    data = response.json()
    if len(data["items"]) == 0:
        return None
    id = data["items"][0]["id"]["videoId"]
    return id



def playlist(playlist_id:str) -> list[str] :

    print(playlist_id)

    ## get Playlist items .ie the videos in the playlist
    link = "https://www.googleapis.com/youtube/v3/playlistItems"
    data = []
    params = {
        "part":"contentDetails",
        "playlistId":playlist_id,
        "key":key,
        "maxResults": 50
    }
    
    response = requests.get(url=link,params=params)
    response.raise_for_status()

    data.append(response.json())


    while "nextPageToken" in data[len(data)-1] != None: # Max results are 50, so look at all pages
        nextPageToken = data[len(data)-1]["nextPageToken"]
        params["pageToken"] = nextPageToken

        response = requests.get(url=link,params=params)
        response.raise_for_status()
        data.append(response.json())

    video_ids = []

    for page in data: # for pages searched
        page_ids=[]

        for video in page["items"]:
            video_id = video["contentDetails"]["videoId"]
            page_ids.append(video_id) # append the video id
        


        ## check if video is avaliable
        link="https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part":"status",
            "key":key,
            "id":",".join(page_ids),
            "maxResults":50
        }

        response = requests.get(url=link,params=params)
        response.raise_for_status()
        
        for video in response.json()["items"]:
            id = video["id"]
            
            if video["status"]["privacyStatus"] != "unlisted": ## dont include unlisted videos
                video_ids.append(id)
    


    print(len(video_ids))
    return video_ids


## returns titles of youtube ids
def get_title(ids:list[str]) -> list[str]:
    link="https://www.googleapis.com/youtube/v3/videos"
    names = []
    while len(ids):
        page = ids[:50]
        ids = ids[50:]
        params={
            "key":key,
            "id":",".join(page),
            "part":"snippet",
            "maxResults":50
        }
        response = requests.get(url=link, params=params)
        response.raise_for_status()
        for vid in response.json()["items"]:
            names.append(vid["snippet"]["title"])
        

    return names



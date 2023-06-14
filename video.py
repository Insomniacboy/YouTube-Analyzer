import requests
from api_key import API_KEY

class Video:
    # Static variables
    VIDEO_STATS_URL = 'https://www.googleapis.com/youtube/v3/videos?part=statistics&part=snippet&key=' + API_KEY + '&id='

    # Object variables
    title = ''
    views = 0
    likes = 0
    url = ''

    def __init__(self, videoId):
        url = Video.VIDEO_STATS_URL + videoId
        response = requests.get(url)
        self.title = response.json()['items'][0]['snippet']['title']
        self.views = response.json()['items'][0]['statistics']['viewCount']
        self.likes = response.json()['items'][0]['statistics']['likeCount']
        self.url = 'https://www.youtube.com/watch?v=' + videoId

    def __str__(self):
        return self.title + " - " + self.views + " - " + self.likes
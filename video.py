import requests
from api_key import API_KEY
import datetime

class Video:
    # Static variables
    VIDEO_STATS_URL = 'https://www.googleapis.com/youtube/v3/videos?part=statistics&part=snippet&key=' + API_KEY + '&id='

    # Object variables
    title = ''
    date = ''
    views = 0
    likes = 0
    url = ''

    def __init__(self, videoId):
        url = Video.VIDEO_STATS_URL + videoId
        response = requests.get(url)
        try:
            self.title = response.json()['items'][0]['snippet']['title']
        except:
            self.title = 'Title not found'
            print(response.json())
        try:
            self.date = datetime.datetime.strptime(response.json()['items'][0]['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        except:
            self.date = 'Date not found'
            print(response.json())
        try:
            self.views = response.json()['items'][0]['statistics']['viewCount']
        except:
            self.views = 'Views not found'
            print(response.json())
        try:
            self.likes = response.json()['items'][0]['statistics']['likeCount']
        except:
            self.likes = 'Likes not found'
            print(response.json())
        try:
            self.url = 'https://www.youtube.com/watch?v=' + videoId
        except:
            self.url = 'URL not found'
            print(response.json())

    def __str__(self):
        return self.title + " - " + self.views + " - " + self.likes
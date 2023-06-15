import requests
from api_key import API_KEY
import datetime

# Code from https://stackoverflow.com/questions/410221/natural-relative-days-in-python
def prettydate(d):
    diff = datetime.datetime.utcnow() - d
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{} minutes ago'.format(int(s/60))
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{} hours ago'.format(int(s/3600))

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
        self.title = response.json()['items'][0]['snippet']['title']
        self.date = prettydate(datetime.datetime.strptime(response.json()['items'][0]['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'))
        self.views = response.json()['items'][0]['statistics']['viewCount']
        self.likes = response.json()['items'][0]['statistics']['likeCount']
        self.url = 'https://www.youtube.com/watch?v=' + videoId

    def __str__(self):
        return self.title + " - " + self.views + " - " + self.likes
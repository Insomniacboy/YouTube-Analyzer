import json
import requests
import os
import datetime
from api_key import API_KEY
import random
import pytube
import re

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
    
def convert_to_seconds(period):
    period = period.replace('PT', '')
    period = period.replace('H', '*60*60+')
    period = period.replace('M', '*60+')
    period = period.replace('S', '')
    if period[len(period) - 1] == '+':
        period = period[:len(period) - 1]
    return eval(period)

class MyVideo:
    # Static variables
    VIDEO_STATS_URL = 'https://www.googleapis.com/youtube/v3/videos?part=statistics&part=snippet&part=contentDetails&key=' + API_KEY + '&id='
    REPORTING_URL = 'https://youtubeanalytics.googleapis.com/v2/reports?metrics=averageViewDuration&ids=channel==MINE&startDate=2020-01-01&endDate='

    VIDEO_SAVE_DIRECTORY = './data/videos'

    # Object variables
    title = ''
    safe_title = ''
    date = ''
    views = 0
    likes = 0
    url = ''
    duration = 0
    retention_rate = 0
    speed_rate = 0

    def __init__(self, videoId, access_token):
        url = MyVideo.VIDEO_STATS_URL + videoId
        response = requests.get(url)

        self.title = response.json()['items'][0]['snippet']['title']
        self.safe_title = re.sub(r'[ :?!\'\".,;(){}\[\]/\\|]', '', self.title)
        self.safe_title = self.safe_title.replace('|', '_')
        self.date = prettydate(datetime.datetime.strptime(response.json()['items'][0]['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'))
        self.views = response.json()['items'][0]['statistics']['viewCount']
        self.likes = response.json()['items'][0]['statistics']['likeCount']
        self.url = 'https://www.youtube.com/watch?v=' + videoId
        duration = response.json()['items'][0]['contentDetails']['duration']
        self.duration = convert_to_seconds(duration) if duration != '' else 0
        url = MyVideo.REPORTING_URL + datetime.datetime.today().strftime('%Y-%m-%d') + '&dimensions=video&filters=video=={}&access_token={}'.format(videoId, access_token)
        self.retention_rate = requests.get(url).json()['rows'][0][1] if len(requests.get(url).json()['rows']) > 0 else 0
        self.speed_rate = float((100 + random.randint(1, 10)) / 100)

    def download(self):
        video = pytube.YouTube(self.url)
        video._title = self.safe_title
        video = video.streams.get_highest_resolution()

        try:
            video.download(MyVideo.VIDEO_SAVE_DIRECTORY)
        except:
            print("Не получилось скачать видео", self.title, self.url)

        print("Видео скачано")


    def __str__(self):
        return self.title + " - " + self.views + " - " + self.likes
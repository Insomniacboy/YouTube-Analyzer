import json
import requests
import os
import datetime
from api_key import API_KEY
import random
import pytube
import re
from oauth import upload_to_youtube
    
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

    def __init__(self, videoId, access_token, isMock = False, duration = 0):
        if not isMock:
            url = MyVideo.VIDEO_STATS_URL + videoId
            response = requests.get(url)

            self.title = response.json()['items'][0]['snippet']['title']
            self.safe_title = re.sub(r'[ :?!\'\".,;(){}\[\]/\\|]', '', self.title)
            self.safe_title = self.safe_title.replace('|', '_')
            self.safe_title = self.safe_title.replace('#', '')
            self.date = datetime.datetime.strptime(response.json()['items'][0]['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
            self.views = response.json()['items'][0]['statistics']['viewCount']
            self.likes = response.json()['items'][0]['statistics']['likeCount']
            self.url = 'https://www.youtube.com/watch?v=' + videoId
            duration = response.json()['items'][0]['contentDetails']['duration']
            self.duration = convert_to_seconds(duration) if duration != '' else 0
            url = MyVideo.REPORTING_URL + datetime.datetime.today().strftime('%Y-%m-%d') + '&dimensions=video&filters=video=={}&access_token={}'.format(videoId, access_token)
            self.retention_rate = requests.get(url).json()['rows'][0][1] if len(requests.get(url).json()['rows']) > 0 else 0
            self.speed_rate = float((100 + random.randint(1, 10)) / 100)
        else:
            self.title = videoId
            self.safe_title = re.sub(r'[ :?!\'\".,;(){}\[\]/\\|]', '', self.title)
            self.safe_title = self.safe_title.replace('|', '_')
            self.safe_title = self.safe_title.replace('#', '')
            self.date = datetime.datetime.today()
            self.views = 0
            self.likes = 0
            self.url = ''
            self.duration = duration
            self.retention_rate = 0
            self.speed_rate = 1.0

    def download(self):
        video = pytube.YouTube(self.url)
        video._title = self.safe_title
        try:
            video = video.streams.get_highest_resolution()
        except Exception as e:
            print(e)
            print("Не получилось скачать видео", self.title, self.url)


        try:
            video.download(MyVideo.VIDEO_SAVE_DIRECTORY)
        except:
            print("Не получилось скачать видео", self.title, self.url)

        print("Видео скачано")

    def downloadable(self):
        video = pytube.YouTube(self.url)
        video._title = self.safe_title
        try:
            video = video.streams.get_highest_resolution()
        except Exception as e:
            print("Нельзя скачать видео", self.title, self.url, e)
            print(e.__traceback__)
            return False
        return True

    def set_speed_rate(self, speed_rate):
        self.speed_rate = speed_rate

    def upload(video_path, title, description):
        upload_to_youtube(video_path, title, description)


    def __str__(self):
        return self.title + " - " + self.views + " - " + self.likes
# Class YouTube
# Description: This class is used to store the information of a YouTube video

import requests
import json
from video import Video
from my_video import MyVideo
from api_key import API_KEY, MY_CHANNEL_ID
from oauth import get_credentials

class YouTube:
    # Static variables
    BASE_URL = 'https://youtube.googleapis.com/youtube/v3/'
    CHANNEL_ID_BY_USERNAME_URL = BASE_URL + 'search?key=' + API_KEY + '&part=snippet&type=channel&q='
    CHANNEL_AUTHOR_BY_ID_URL = BASE_URL + 'channels?key=' + API_KEY + '&id='
    PLAYLIST_URL = 'https://www.googleapis.com/youtube/v3/playlists'
    VIDEO_URL = 'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&order=date&key=' + API_KEY + '&channelId='

    # Object variables
    author = ''
    channelId = ''
    url = ''
    access_token = ''
    videos = []

    def __init__(self, *args):
        sample_size = 50
        if len(args) == 1:
            sample_size = args[0] * 4
            self.channelId = MY_CHANNEL_ID
            self.author = YouTube.get_channel_author_by_id(self, MY_CHANNEL_ID)
            self.url = 'https://www.youtube.com/channel/' + MY_CHANNEL_ID
            self.videos = YouTube.get_my_videos(self, sample_size)
        else:
            sample_size = args[1]
            self.author = YouTube.get_channel_author(self, args[0])
            # delete @ symbol
            if self.author[0] == '@':
                self.author = self.author[1:]
            self.url = args[0]
            if self.author != 'Invalid URL' and self.channelId == '':
                self.channelId = YouTube.get_channel_id_by_author(self.author)
            self.videos = YouTube.get_videos(self, sample_size)
            self.videos.reverse()

    def get_channel_author(self, url):
        try:
            _url = url.split('/')
            if len(_url) == 5:
                self.channelId = _url[4]
                return YouTube.get_channel_author_by_id(self, self.channelId)
            return _url[3]
        except:
           return 'Invalid URL'
                
    def get_channel_author_by_id(self, channelId):
        url = YouTube.CHANNEL_AUTHOR_BY_ID_URL + channelId + '&part=snippet'
        response = requests.get(url)
        return response.json()['items'][0]['snippet']['title']

    def get_channel_id_by_author(username):
        url = YouTube.CHANNEL_ID_BY_USERNAME_URL + username
        response = requests.get(url)
        return response.json()['items'][0]['id']['channelId']
    
    def get_videos(self, sample_size):
        videos_list = []
        url = YouTube.VIDEO_URL + self.channelId + '&maxResults=' + str(sample_size)
        response = requests.get(url)
        for item in response.json()['items']:
            video = Video(item['id']['videoId'])
            videos_list.append(video)
        return videos_list
    
    def get_my_videos(self, sample_size):
        access_token = get_credentials().token
        self.access_token = access_token
        videos_list = []
        url = YouTube.VIDEO_URL + self.channelId + '&maxResults=' + str(sample_size)
        response = requests.get(url)

        times = (response.json()['pageInfo']['totalResults'] + response.json()['pageInfo']['resultsPerPage'] - 1) // response.json()['pageInfo']['resultsPerPage']
        total_results = response.json()['pageInfo']['totalResults']
        processed_results = 0

        for i in range(times):
            for item in response.json()['items']:
                video = MyVideo(item['id']['videoId'], access_token)
                if video.duration > 60 and video.duration <= 180:
                    videos_list.append(video)
                processed_results += 1
                print('Обработано: {}/{}'.format(processed_results, total_results))
            
            url = YouTube.VIDEO_URL + self.channelId + '&maxResults=' + str(sample_size) + '&pageToken=' + response.json()['nextPageToken']

        return videos_list
    
    def appendVideo(self, video_id):
        video = MyVideo(video_id, self.access_token)
        self.videos.append(video)

    def uploadVideo(video_path, title, description):
        MyVideo.upload(video_path, title, description)

    def __str__(self):
        return self.author + " - " + self.url + " - " + self.channelId
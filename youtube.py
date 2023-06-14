# Class YouTube
# Description: This class is used to store the information of a YouTube video

import requests
import json
from video import Video
from api_key import API_KEY

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
    videos = []

    def __init__(self, url, sample_size=50):
        self.author = YouTube.get_channel_author(self, url)
        # delete @ symbol
        if self.author[0] == '@':
            self.author = self.author[1:]
        self.url = url
        if self.author != 'Invalid URL' and self.channelId == '':
            self.channelId = YouTube.get_channel_id_by_author(self.author)
        self.videos = YouTube.get_videos(self, sample_size)

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

    def __str__(self):
        return self.author + " - " + self.url + " - " + self.channelId
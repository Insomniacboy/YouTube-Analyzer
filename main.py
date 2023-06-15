# Description: Main file for the project

# Imports
import requests
import json
import os
from youtube import YouTube
import re
import csv
import locale
from decimal import Decimal

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

def print_progress_bar(nProcessed, nTotal, barLength=50):
    percent = float(nProcessed) / nTotal
    arrow = '-' * int(round(percent * barLength)-1) + '>'
    spaces = ' ' * (barLength - len(arrow))
    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent*100), end='\r')

# Main function
if __name__ == '__main__':
    # set locale
    locale.setlocale(locale.LC_ALL, 'en_US')
    # get sample size
    sample_size = 50
    if os.path.exists('sample_size.txt'):
        with open('sample_size.txt', 'r') as f:
            sample_size = int(f.read())
    
    # create nProcessed and nTotal
    nProcessed = 0
    nTotal = 0
    with open('channels.txt', 'r') as f:
        nTotal = len(f.readlines())

    # read from channels.txt and create object for each channel
    channels = []
    with open('channels.txt', 'r') as f:
        for line in f:
            channels.append(YouTube(line.strip(), sample_size))
            nProcessed += 1
            print_progress_bar(nProcessed, nTotal)

    # Write to Excel file
    csv_columns = ['Channel', 'Video', 'Views', 'Likes', 'URL', 'Date']
    with open('output.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()
        for channel in channels:
            for video in channel.videos:
                writer.writerow({'Channel': channel.author, 'Video': emoji_pattern.sub(r'', video.title), 'Views': "{:,}".format(int(video.views)), 'Likes': "{:,}".format(int(video.likes)), 'URL': video.url, 'Date': video.date})